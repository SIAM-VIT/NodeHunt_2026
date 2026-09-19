import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, JSON, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from data.nodes_config import START_NODE_ID


class Team(Base):
    """Represents a team session."""

    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    team_name: Mapped[str] = mapped_column(String(120), default="Unnamed Team", unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    current_node_id: Mapped[str] = mapped_column(String(20), default=START_NODE_ID)
    path: Mapped[list] = mapped_column(JSON, default=list)
    total_score: Mapped[int] = mapped_column(Integer, default=0)

    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    lock_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)

    moves: Mapped[List["TeamMove"]] = relationship(
        "TeamMove", back_populates="team", order_by="TeamMove.moved_at", cascade="all, delete-orphan"
    )
    progress: Mapped[List["TeamNodeProgress"]] = relationship(
        "TeamNodeProgress", back_populates="team", cascade="all, delete-orphan"
    )


class TeamNodeProgress(Base):
    """Per-team, per-node attempt and scoring state."""

    __tablename__ = "team_node_progress"
    __table_args__ = (UniqueConstraint("team_id", "node_id", name="uq_team_node_progress"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    node_id: Mapped[str] = mapped_column(String(20))

    attempts_used: Mapped[int] = mapped_column(Integer, default=0)
    solved: Mapped[bool] = mapped_column(Boolean, default=False)
    exhausted: Mapped[bool] = mapped_column(Boolean, default=False)
    movement_unlocked: Mapped[bool] = mapped_column(Boolean, default=False)
    points_awarded: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    solved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    team: Mapped["Team"] = relationship("Team", back_populates="progress")


class TeamMove(Base):
    """Records every left / right / continue node transition."""

    __tablename__ = "team_moves"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    from_node: Mapped[str] = mapped_column(String(20))
    to_node: Mapped[str] = mapped_column(String(20))
    direction: Mapped[str] = mapped_column(String(20))
    moved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    team: Mapped["Team"] = relationship("Team", back_populates="moves")