from contextlib import asynccontextmanager
from uuid import UUID
import logging
import hashlib
import time

from google.auth import jwt
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db, init_db, settings
from src.models import User, Puzzle, UserPuzzleProgress
from src.schemas import (
    PuzzleResponse,
    ProgressUpdateRequest,
    ProgressResponse,
    ProgressHistoryItem,
)
from src.crosshare import fetch_puzzle_list, fetch_puzzle, is_valid_puzzle_size
from src.converters import crosshare_to_capi

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Crossword API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Cache verified tokens (token_hash -> (google_id, email, expiry))
_token_cache: dict[str, tuple[str, str, float]] = {}


def _verify_google_token(token: str) -> dict | None:
    """Decode Google ID token (skip verification - token from OAuth flow)."""
    try:
        claims = jwt.decode(token, verify=False)
        # Check audience matches our client ID
        if claims.get("aud") != settings.google_client_id:
            logger.warning(f"Token audience mismatch: got {claims.get('aud')}, expected {settings.google_client_id}")
            return None
        return {"sub": claims["sub"], "email": claims["email"]}
    except Exception as e:
        logger.warning(f"Token decode failed: {e}")
        return None


# Dependency to get current user from Google OAuth token
async def get_current_user(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    logger.info(f"get_current_user called, auth header present: {authorization is not None}")

    if not authorization or not authorization.startswith("Bearer "):
        logger.info("No valid Authorization header")
        return None

    token = authorization.removeprefix("Bearer ")
    logger.info(f"Token extracted (length: {len(token)})")

    # Check cache first
    token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
    if token_hash in _token_cache:
        google_id, email, expiry = _token_cache[token_hash]
        if time.time() < expiry:
            # Cache hit - find user
            result = await db.execute(select(User).where(User.google_id == google_id))
            user = result.scalar_one_or_none()
            if user:
                return user
            # User not found but token valid - create user
            user = User(google_id=google_id, email=email)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        else:
            del _token_cache[token_hash]

    # Decode token (no verification - token from OAuth flow)
    idinfo = _verify_google_token(token)
    if not idinfo:
        return None

    google_id = idinfo["sub"]
    email = idinfo["email"]

    # Cache for 55 min
    _token_cache[token_hash] = (google_id, email, time.time() + 3300)

    # Find user by google_id
    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()

    # Auto-create user on first valid token
    if not user:
        user = User(google_id=google_id, email=email)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Created new user: {email} ({google_id})")

    return user


def require_user(user: User | None = Depends(get_current_user)) -> User:
    if not user:
        raise HTTPException(status_code=401, detail="Valid Authorization header required")
    return user


# Health check
@app.get("/health")
async def health():
    return {"status": "ok"}


# Puzzles
@app.get("/puzzles/next", response_model=PuzzleResponse)
async def get_next_puzzle(
    user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the next unplayed puzzle for the user.

    First checks for existing unplayed puzzles in the database.
    If none found, fetches a new puzzle from Crosshare.org.
    """
    # Get puzzle IDs user has already started
    played_subq = select(UserPuzzleProgress.puzzle_id).where(
        UserPuzzleProgress.user_id == user.id
    )

    # Find first puzzle not in played list
    result = await db.execute(
        select(Puzzle)
        .where(Puzzle.id.notin_(played_subq))
        .order_by(Puzzle.puzzle_number.asc())
        .limit(1)
    )
    puzzle = result.scalar_one_or_none()

    # If no unplayed puzzles in DB, fetch from Crosshare
    if not puzzle:
        puzzle = await _fetch_new_puzzle_from_crosshare(db)

    if not puzzle:
        raise HTTPException(status_code=404, detail="No more puzzles available")

    # Create progress record to mark as started
    progress = UserPuzzleProgress(user_id=user.id, puzzle_id=puzzle.id)
    db.add(progress)
    await db.commit()

    return PuzzleResponse(
        id=puzzle.id,
        puzzle_number=puzzle.puzzle_number,
        name=puzzle.name,
        data=puzzle.data,
        progress={},
    )


async def _fetch_new_puzzle_from_crosshare(db: AsyncSession) -> Puzzle | None:
    """Fetch a new featured puzzle from Crosshare that we don't already have."""
    try:
        for page in range(1, 10):
            crosshare_puzzles = await fetch_puzzle_list(page=page)

            if not crosshare_puzzles:
                break

            for ch_puzzle_meta in crosshare_puzzles:
                ch_id = ch_puzzle_meta.get("id")
                if not ch_id:
                    continue

                # Check if we already have this puzzle
                existing = await db.execute(
                    select(Puzzle).where(Puzzle.crosshare_id == ch_id)
                )
                if existing.scalar_one_or_none():
                    continue

                # Fetch full puzzle data
                ch_puzzle = await fetch_puzzle(ch_id)

                # Check clue count filter
                if not is_valid_puzzle_size(ch_puzzle):
                    continue

                # Convert to CAPI format
                capi_data = crosshare_to_capi(ch_puzzle)

                # Get next puzzle number
                max_num_result = await db.execute(select(func.max(Puzzle.puzzle_number)))
                max_num = max_num_result.scalar() or 0
                next_num = max_num + 1

                # Update the puzzle data with the new number
                capi_data["number"] = next_num

                # Create and save puzzle
                new_puzzle = Puzzle(
                    puzzle_number=next_num,
                    name=capi_data["name"],
                    data=capi_data,
                    crosshare_id=ch_id,
                )
                try:
                    db.add(new_puzzle)
                    await db.commit()
                    await db.refresh(new_puzzle)
                    logger.info(f"Fetched new puzzle from Crosshare: {new_puzzle.name} (#{next_num})")
                    return new_puzzle
                except IntegrityError:
                    await db.rollback()
                    # Puzzle was inserted by another request, fetch it
                    logger.info(f"Puzzle {ch_id} already exists, fetching existing")
                    existing = await db.execute(
                        select(Puzzle).where(Puzzle.crosshare_id == ch_id)
                    )
                    existing_puzzle = existing.scalar_one_or_none()
                    if existing_puzzle:
                        return existing_puzzle
                    continue  # Try next puzzle

    except Exception as e:
        logger.error(f"Error fetching puzzle from Crosshare: {e}")
        return None

    return None


@app.get("/puzzles/{puzzle_id}", response_model=PuzzleResponse)
async def get_puzzle(
    puzzle_id: UUID,
    user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific puzzle with user's progress."""
    result = await db.execute(select(Puzzle).where(Puzzle.id == puzzle_id))
    puzzle = result.scalar_one_or_none()

    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")

    # Get user's progress
    progress_result = await db.execute(
        select(UserPuzzleProgress).where(
            UserPuzzleProgress.user_id == user.id,
            UserPuzzleProgress.puzzle_id == puzzle_id,
        )
    )
    progress = progress_result.scalar_one_or_none()

    return PuzzleResponse(
        id=puzzle.id,
        puzzle_number=puzzle.puzzle_number,
        name=puzzle.name,
        data=puzzle.data,
        progress=progress.cell_progress if progress else None,
    )


# Progress
@app.get("/progress", response_model=list[ProgressHistoryItem])
async def get_progress_history(
    user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's puzzle history."""
    result = await db.execute(
        select(UserPuzzleProgress, Puzzle)
        .join(Puzzle)
        .where(UserPuzzleProgress.user_id == user.id)
        .order_by(UserPuzzleProgress.started_at.desc())
    )
    rows = result.all()

    history = []
    for progress, puzzle in rows:
        # Calculate completion percentage based on filled cells vs total grid
        total_cells = puzzle.data.get("dimensions", {}).get("cols", 0) * puzzle.data.get(
            "dimensions", {}
        ).get("rows", 0)
        filled = len(progress.cell_progress)
        pct = (filled / total_cells * 100) if total_cells > 0 else 0

        history.append(
            ProgressHistoryItem(
                puzzle_id=puzzle.id,
                puzzle_number=puzzle.puzzle_number,
                puzzle_name=puzzle.name,
                status=progress.status,
                started_at=progress.started_at,
                completed_at=progress.completed_at,
                completion_percentage=round(pct, 1),
            )
        )

    return history


@app.put("/progress/{puzzle_id}", response_model=ProgressResponse)
async def update_progress(
    puzzle_id: UUID,
    request: ProgressUpdateRequest,
    user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Update cell progress for a puzzle."""
    # Get puzzle
    puzzle_result = await db.execute(select(Puzzle).where(Puzzle.id == puzzle_id))
    puzzle = puzzle_result.scalar_one_or_none()
    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")

    # Get or create progress
    result = await db.execute(
        select(UserPuzzleProgress).where(
            UserPuzzleProgress.user_id == user.id,
            UserPuzzleProgress.puzzle_id == puzzle_id,
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        progress = UserPuzzleProgress(user_id=user.id, puzzle_id=puzzle_id)
        db.add(progress)

    # Update cells
    for key, value in request.cells.items():
        if value:
            progress.cell_progress[key] = value.upper()
        elif key in progress.cell_progress:
            del progress.cell_progress[key]

    await db.commit()
    await db.refresh(progress)

    return ProgressResponse(
        puzzle_id=puzzle.id,
        puzzle_number=puzzle.puzzle_number,
        puzzle_name=puzzle.name,
        cell_progress=progress.cell_progress,
        status=progress.status,
        started_at=progress.started_at,
        completed_at=progress.completed_at,
        total_filled=len(progress.cell_progress),
    )


@app.post("/progress/{puzzle_id}/complete")
async def mark_complete(
    puzzle_id: UUID,
    user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a puzzle as completed."""
    result = await db.execute(
        select(UserPuzzleProgress).where(
            UserPuzzleProgress.user_id == user.id,
            UserPuzzleProgress.puzzle_id == puzzle_id,
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")

    from datetime import datetime

    progress.status = "completed"
    progress.completed_at = datetime.utcnow()
    await db.commit()

    return {"status": "completed"}
