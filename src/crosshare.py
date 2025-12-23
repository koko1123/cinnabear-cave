"""Crosshare.org puzzle fetching service."""
import json
import httpx
from bs4 import BeautifulSoup

# Clue count filter: 60 < num_clues < 80
MIN_CLUES = 60
MAX_CLUES = 80


async def fetch_puzzle_list(page: int = 1) -> list[dict]:
    """Fetch list of featured puzzles from Crosshare.

    Args:
        page: Page number for pagination (1-indexed)

    Returns list of puzzle metadata dicts with 'id' and other fields.
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(f"https://crosshare.org/featured/{page}", timeout=30.0)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")

        if not script or not script.string:
            raise ValueError("Could not find __NEXT_DATA__ in Crosshare page")

        data = json.loads(script.string)
        puzzles = data.get("props", {}).get("pageProps", {}).get("puzzles", [])

        return puzzles


def get_clue_count(puzzle: dict) -> int:
    """Get the number of clues in a puzzle."""
    clues = puzzle.get("clues", [])
    return len(clues)


def is_valid_puzzle_size(puzzle: dict) -> bool:
    """Check if puzzle has valid clue count (60 < clues < 80)."""
    clue_count = get_clue_count(puzzle)
    return MIN_CLUES < clue_count < MAX_CLUES


async def fetch_puzzle(puzzle_id: str) -> dict:
    """Fetch a single puzzle from Crosshare by ID.

    Returns the full puzzle data dict.
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        url = f"https://crosshare.org/crosswords/{puzzle_id}"
        resp = await client.get(url, timeout=30.0)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")

        if not script or not script.string:
            raise ValueError(f"Could not find __NEXT_DATA__ for puzzle {puzzle_id}")

        data = json.loads(script.string)
        puzzle = data.get("props", {}).get("pageProps", {}).get("puzzle")

        if not puzzle:
            raise ValueError(f"No puzzle data found for {puzzle_id}")

        # Add the ID to the puzzle data if not present
        if "id" not in puzzle:
            puzzle["id"] = puzzle_id

        return puzzle
