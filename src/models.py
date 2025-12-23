import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    progress: Mapped[list["UserPuzzleProgress"]] = relationship(back_populates="user")


class Puzzle(Base):
    __tablename__ = "puzzles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    puzzle_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)  # Full CAPICrossword object
    crosshare_id: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user_progress: Mapped[list["UserPuzzleProgress"]] = relationship(back_populates="puzzle")


class UserPuzzleProgress(Base):
    __tablename__ = "user_puzzle_progress"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    puzzle_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("puzzles.id"), nullable=False)
    cell_progress: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)  # {"x,y": "A", ...}
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="in_progress")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="progress")
    puzzle: Mapped["Puzzle"] = relationship(back_populates="user_progress")

    __table_args__ = (UniqueConstraint("user_id", "puzzle_id", name="uq_user_puzzle"),)
