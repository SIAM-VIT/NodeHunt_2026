import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from data.nodes_config import MAX_ATTEMPTS, NODES, get_available_routes
from database import get_db
from schemas import NodeQuestion
from routers.utils import attempts_left, ensure_active_team, get_or_create_progress, get_team_or_404, score_available_for_attempts

router = APIRouter(prefix="/api/node", tags=["nodes"])


@router.get("/{node_id}", response_model=NodeQuestion)
async def get_node(
    node_id: str,
    session_id: uuid.UUID = Query(...),
    index: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Return safe node content plus team progress for this node."""
    node = NODES.get(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")

    team = await get_team_or_404(db, session_id)
    ensure_active_team(team)

    if team.current_node_id != node_id:
        raise HTTPException(status_code=400, detail=f"Team is on '{team.current_node_id}', not '{node_id}'")

    progress = await get_or_create_progress(db, team, node_id)
    await db.commit()

    q_data = node.get("question", {})
    available_sets = [q_data[key] for key in ("set1", "set2", "set3") if key in q_data]
    max_questions = len(available_sets)
    if max_questions == 0:
        question_text = ""
        index = 0
    else:
        index = min(index, max_questions - 1)
        question_text = available_sets[index]

    return NodeQuestion(
        node_id=node_id,
        node_type=node.get("type", "D"),
        difficulty=node.get("difficulty", "easy"),
        question_text=question_text,
        current_index=index,
        max_questions=max_questions,
        attempts_used=progress.attempts_used,
        attempts_left=attempts_left(progress.attempts_used),
        score_available=score_available_for_attempts(progress.attempts_used),
        movement_unlocked=progress.movement_unlocked,
        is_terminal=bool(node.get("is_terminal", False)),
        team_score=team.total_score,
        is_locked=team.is_locked,
        available_routes=get_available_routes(node_id) if progress.movement_unlocked and not node.get("is_terminal") else [],
    )
