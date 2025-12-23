from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


# Puzzles
class PuzzleResponse(BaseModel):
    id: UUID
    puzzle_number: int
    name: str
    data: dict  # Full CAPICrossword object
    progress: dict | None = None  # User's cell progress if exists


class PuzzleListItem(BaseModel):
    id: UUID
    puzzle_number: int
    name: str


# Progress
class ProgressUpdateRequest(BaseModel):
    cells: dict[str, str]  # {"x,y": "A", ...}


class ProgressResponse(BaseModel):
    puzzle_id: UUID
    puzzle_number: int
    puzzle_name: str
    cell_progress: dict[str, str]
    status: str
    started_at: datetime
    completed_at: datetime | None
    total_filled: int


class ProgressHistoryItem(BaseModel):
    puzzle_id: UUID
    puzzle_number: int
    puzzle_name: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    completion_percentage: float
