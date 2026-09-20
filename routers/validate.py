from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from data.nodes_config import MAX_ATTEMPTS, NODES, SCORE_BY_ATTEMPT, get_available_routes, is_correct_answer
from database import get_db
from schemas import MoveRequest, MoveResponse, ValidateRequest, ValidateResponse
from models import TeamMove
from routers.utils import attempts_left, ensure_active_team, get_or_create_progress, get_team_or_404, now_utc, score_available_for_attempts

router = APIRouter(prefix="/api", tags=["validate"])


@router.post("/validate", response_model=ValidateResponse)
async def validate_answer(body: ValidateRequest, db: AsyncSession = Depends(get_db)):
    """Validate the current node answer or volunteer passcode.

    Awards score and unlocks movement. After three wrong attempts,
    movement unlocks with 0 points.
    """
    node = NODES.get(body.node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{body.node_id}' not found")

    team = await get_team_or_404(db, body.session_id)
    ensure_active_team(team)

    if team.current_node_id != body.node_id:
        raise HTTPException(status_code=400, detail=f"Team is on '{team.current_node_id}', not '{body.node_id}'")

    progress = await get_or_create_progress(db, team, body.node_id)
    is_terminal = bool(node.get("is_terminal", False))

    # Idempotent response if frontend retries after state is already unlocked.
    if progress.movement_unlocked:
        return ValidateResponse(
            correct=progress.solved,
            attempts_used=progress.attempts_used,
            attempts_left=attempts_left(progress.attempts_used),
            score_available=score_available_for_attempts(progress.attempts_used),
            movement_unlocked=True,
            points_awarded=progress.points_awarded,
            total_score=team.total_score,
            is_terminal=is_terminal,
            completed=team.completed,
            next_node_id="__winner__" if team.completed else None,
            available_routes=[] if is_terminal else get_available_routes(body.node_id),
            message="Movement already unlocked." if not team.completed else "Hunt completed.",
        )

    if progress.attempts_used >= MAX_ATTEMPTS:
        raise HTTPException(status_code=400, detail="No attempts left")

    progress.attempts_used += 1
    input_ans = body.answer.strip().lower()
    is_passcode_success = input_ans in settings.success_passcodes
    correct = is_passcode_success or is_correct_answer(body.node_id, body.answer)

    if correct:
        points = SCORE_BY_ATTEMPT.get(progress.attempts_used, 0)
        progress.solved = True
        progress.exhausted = False
        progress.movement_unlocked = True
        progress.points_awarded = points
        progress.solved_at = now_utc()
        team.total_score += points

        if is_terminal:
            team.completed = True
            team.completed_at = now_utc()

        await db.commit()
        await db.refresh(team)

        return ValidateResponse(
            correct=True,
            attempts_used=progress.attempts_used,
            attempts_left=attempts_left(progress.attempts_used),
            score_available=0,
            movement_unlocked=True,
            points_awarded=points,
            total_score=team.total_score,
            is_terminal=is_terminal,
            completed=team.completed,
            next_node_id="__winner__" if team.completed else None,
            available_routes=[] if is_terminal else get_available_routes(body.node_id),
            message="Hunt completed." if team.completed else "Correct. Choose your path.",
        )

    # Incorrect answer.
    if progress.attempts_used >= MAX_ATTEMPTS:
        progress.exhausted = True
        progress.movement_unlocked = True
        progress.points_awarded = 0

        if is_terminal:
            team.completed = True
            team.completed_at = now_utc()

        await db.commit()
        await db.refresh(team)

        return ValidateResponse(
            correct=False,
            attempts_used=progress.attempts_used,
            attempts_left=0,
            score_available=0,
            movement_unlocked=True,
            points_awarded=0,
            total_score=team.total_score,
            is_terminal=is_terminal,
            completed=team.completed,
            next_node_id="__winner__" if team.completed else None,
            available_routes=[] if is_terminal else get_available_routes(body.node_id),
            message=(
                "No attempts left. Final node completed with 0 points."
                if team.completed
                else "No attempts left. You earned 0 points, but your path is unlocked."
            ),
        )

    await db.commit()

    return ValidateResponse(
        correct=False,
        attempts_used=progress.attempts_used,
        attempts_left=attempts_left(progress.attempts_used),
        score_available=score_available_for_attempts(progress.attempts_used),
        movement_unlocked=False,
        points_awarded=0,
        total_score=team.total_score,
        is_terminal=is_terminal,
        completed=False,
        available_routes=[],
        message="Incorrect answer. Try again.",
    )


@router.post("/move", response_model=MoveResponse)
async def move_team(body: MoveRequest, db: AsyncSession = Depends(get_db)):
    """Move left/right after the current node has unlocked movement."""
    node = NODES.get(body.node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{body.node_id}' not found")

    team = await get_team_or_404(db, body.session_id)
    ensure_active_team(team)

    if team.current_node_id != body.node_id:
        raise HTTPException(status_code=400, detail=f"Team is on '{team.current_node_id}', not '{body.node_id}'")

    if node.get("is_terminal"):
        raise HTTPException(status_code=400, detail="Cannot move from a terminal node")

    progress = await get_or_create_progress(db, team, body.node_id)
    if not progress.movement_unlocked:
        raise HTTPException(status_code=403, detail="Movement is not unlocked for this node")

    routes = node.get("routes", {})
    next_node_id = routes.get(body.direction)
    if not next_node_id:
        raise HTTPException(status_code=400, detail="Invalid direction for this node")

    move = TeamMove(
        team_id=team.id,
        from_node=body.node_id,
        to_node=next_node_id,
        direction=body.direction,
    )
    db.add(move)

    team.current_node_id = next_node_id
    path = list(team.path or [])
    if not path or path[-1] != next_node_id:
        path.append(next_node_id)
    team.path = path

    await db.commit()
    await db.refresh(team)

    return MoveResponse(session_id=team.id, next_node_id=next_node_id, current_node_id=team.current_node_id)
