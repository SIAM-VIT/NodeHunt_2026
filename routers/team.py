import hashlib
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from data.nodes_config import START_NODE_ID
from database import get_db
from models import Team
from schemas import TeamCreateRequest, TeamLoginRequest, TeamNameUpdateRequest, TeamOut, TeamSessionResponse, TeamStartRequest
from routers.utils import get_team_or_404, now_utc, team_status

router = APIRouter(prefix="/api/team", tags=["team"])


def hash_password(password: str | None) -> str | None:
    if not password:
        return None
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@router.post("", response_model=TeamSessionResponse)
async def create_team(body: TeamCreateRequest, db: AsyncSession = Depends(get_db)):
    team = Team(
        team_name=body.team_name.strip(),
        password_hash=hash_password(body.password),
        current_node_id=START_NODE_ID,
        path=[],
        total_score=0,
    )
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return TeamSessionResponse(
        session_id=team.id,
        team_name=team.team_name,
        status=team_status(team),
        current_node_id=None,
    )


@router.post("/login", response_model=TeamSessionResponse)
async def login_team(body: TeamLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team).where(func.lower(Team.team_name) == body.team_name.strip().lower()))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found. Please register or contact an organizer.")

    if team.is_locked:
        raise HTTPException(status_code=423, detail=team.lock_reason or "Team is locked by admin")

    if team.password_hash:
        input_hash = hash_password(body.password)
        if input_hash != team.password_hash:
            raise HTTPException(status_code=401, detail="Invalid team password")

    if team.started_at is None:
        team.started_at = now_utc()
        team.current_node_id = START_NODE_ID
        team.path = [START_NODE_ID]
        await db.commit()
        await db.refresh(team)

    return TeamSessionResponse(
        session_id=team.id,
        team_name=team.team_name,
        status=team_status(team),
        current_node_id=team.current_node_id or START_NODE_ID,
    )


@router.post("/start", response_model=TeamSessionResponse)
async def start_team(body: TeamStartRequest, db: AsyncSession = Depends(get_db)):
    team = await get_team_or_404(db, body.session_id)
    if team.is_locked:
        raise HTTPException(status_code=423, detail=team.lock_reason or "Team is locked")
    if team.completed:
        raise HTTPException(status_code=400, detail="Team has already completed the hunt")

    if team.started_at is None:
        team.started_at = now_utc()
        team.current_node_id = START_NODE_ID
        team.path = [START_NODE_ID]

    await db.commit()
    await db.refresh(team)
    return TeamSessionResponse(
        session_id=team.id,
        team_name=team.team_name,
        status=team_status(team),
        current_node_id=team.current_node_id,
    )


@router.patch("/name", response_model=TeamSessionResponse)
async def update_team_name(body: TeamNameUpdateRequest, db: AsyncSession = Depends(get_db)):
    team = await get_team_or_404(db, body.session_id)
    if team.started_at is not None:
        raise HTTPException(status_code=403, detail="Team name can only be changed by admin after game starts")
    team.team_name = body.team_name.strip()
    await db.commit()
    await db.refresh(team)
    return TeamSessionResponse(
        session_id=team.id,
        team_name=team.team_name,
        status=team_status(team),
        current_node_id=team.current_node_id if team.started_at else None,
    )


@router.get("/{session_id}", response_model=TeamOut)
async def get_team_detail(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Team)
        .options(selectinload(Team.moves), selectinload(Team.progress))
        .where(Team.id == session_id)
    )
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team session not found")
    return team

