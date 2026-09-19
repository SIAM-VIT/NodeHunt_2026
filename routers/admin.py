import uuid

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config import settings
from database import get_db
from models import Team
from schemas import AdminTeamNameRequest, LockTeamRequest, TeamOut

router = APIRouter(prefix="/api/admin", tags=["admin"])


def verify_admin(x_admin_secret: str = Header(...)):
    if x_admin_secret != settings.ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")


@router.get("/teams", response_model=list[TeamOut])
async def list_teams(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_admin),
):
    result = await db.execute(
        select(Team)
        .options(selectinload(Team.moves), selectinload(Team.progress))
        .order_by(Team.created_at)
    )
    return result.scalars().all()


@router.patch("/team/{team_id}/lock")
async def set_team_lock(
    team_id: uuid.UUID,
    body: LockTeamRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_admin),
):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    team.is_locked = body.locked
    team.lock_reason = body.reason if body.locked else None
    await db.commit()
    await db.refresh(team)
    return {"id": team.id, "is_locked": team.is_locked, "lock_reason": team.lock_reason}


@router.patch("/team/{team_id}/name")
async def admin_update_team_name(
    team_id: uuid.UUID,
    body: AdminTeamNameRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_admin),
):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    team.team_name = body.team_name.strip()
    await db.commit()
    await db.refresh(team)
    return {"id": team.id, "team_name": team.team_name}


@router.delete("/teams", status_code=204)
async def reset_all_teams(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_admin),
):
    result = await db.execute(select(Team))
    for team in result.scalars().all():
        await db.delete(team)
    await db.commit()
