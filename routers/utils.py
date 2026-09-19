import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.nodes_config import MAX_ATTEMPTS, SCORE_BY_ATTEMPT, START_NODE_ID
from models import Team, TeamNodeProgress


def team_status(team: Team) -> str:
    if team.is_locked:
        return "LOCKED"
    if team.completed:
        return "COMPLETED"
    if team.started_at is not None:
        return "ACTIVE"
    return "REGISTERED"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def get_team_or_404(db: AsyncSession, session_id: uuid.UUID) -> Team:
    result = await db.execute(select(Team).where(Team.id == session_id))
    team = result.scalar_one_or_none()
    if team is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return team


async def get_or_create_progress(db: AsyncSession, team: Team, node_id: str) -> TeamNodeProgress:
    result = await db.execute(
        select(TeamNodeProgress).where(
            TeamNodeProgress.team_id == team.id,
            TeamNodeProgress.node_id == node_id,
        )
    )
    progress = result.scalar_one_or_none()
    if progress is not None:
        return progress

    progress = TeamNodeProgress(team_id=team.id, node_id=node_id)
    db.add(progress)
    await db.flush()
    return progress


def score_available_for_attempts(attempts_used: int) -> int:
    next_attempt = attempts_used + 1
    return SCORE_BY_ATTEMPT.get(next_attempt, 0) if next_attempt <= MAX_ATTEMPTS else 0


def attempts_left(attempts_used: int) -> int:
    return max(0, MAX_ATTEMPTS - attempts_used)


def ensure_active_team(team: Team):
    if team.is_locked:
        raise HTTPException(status_code=423, detail=team.lock_reason or "Team is locked")
    if team.completed:
        raise HTTPException(status_code=400, detail="Team has already completed the hunt")
    if team.started_at is None:
        # Backwards/event convenience: first gameplay call activates team.
        team.started_at = now_utc()
        team.current_node_id = team.current_node_id or START_NODE_ID
        if not team.path:
            team.path = [team.current_node_id]
