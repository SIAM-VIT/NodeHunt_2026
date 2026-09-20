import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

NodeType = Literal["D", "C", "Q", "R"]
Difficulty = Literal["easy", "medium", "hard"]
Direction = Literal["left", "right"]
TeamStatus = Literal["REGISTERED", "ACTIVE", "COMPLETED", "LOCKED"]


class RoutePreview(BaseModel):
    direction: Direction
    type: NodeType
    difficulty: Difficulty
    terminal: bool = False


class TeamCreateRequest(BaseModel):
    team_name: str = Field(min_length=1, max_length=120)
    password: str | None = Field(default=None, min_length=1, max_length=120)


class TeamLoginRequest(BaseModel):
    team_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=1, max_length=120)


class TeamStartRequest(BaseModel):
    session_id: uuid.UUID


class TeamNameUpdateRequest(BaseModel):
    session_id: uuid.UUID
    team_name: str = Field(min_length=1, max_length=120)


class TeamSessionResponse(BaseModel):
    session_id: uuid.UUID
    team_name: str
    status: TeamStatus
    current_node_id: str | None = None


class NodeQuestion(BaseModel):
    node_id: str
    node_type: NodeType
    difficulty: Difficulty
    question_text: str
    current_index: int
    max_questions: int
    attempts_used: int
    attempts_left: int
    score_available: int
    movement_unlocked: bool
    is_terminal: bool
    team_score: int
    is_locked: bool
    available_routes: list[RoutePreview] = []


class ValidateRequest(BaseModel):
    session_id: uuid.UUID
    node_id: str
    answer: str


class ValidateResponse(BaseModel):
    correct: bool
    attempts_used: int
    attempts_left: int = 0
    score_available: int = 0
    movement_unlocked: bool
    points_awarded: int
    total_score: int
    is_terminal: bool = False
    completed: bool = False
    next_node_id: str | None = None
    available_routes: list[RoutePreview] = []
    message: str


class MoveRequest(BaseModel):
    session_id: uuid.UUID
    node_id: str
    direction: Direction


class MoveResponse(BaseModel):
    session_id: uuid.UUID
    next_node_id: str
    current_node_id: str


class LockTeamRequest(BaseModel):
    locked: bool
    reason: str | None = None


class AdminTeamNameRequest(BaseModel):
    team_name: str = Field(min_length=1, max_length=120)


class MoveOut(BaseModel):
    from_node: str
    to_node: str
    direction: str
    moved_at: datetime

    model_config = {"from_attributes": True}


class ProgressOut(BaseModel):
    node_id: str
    attempts_used: int
    solved: bool
    exhausted: bool
    movement_unlocked: bool
    points_awarded: int

    model_config = {"from_attributes": True}


class TeamOut(BaseModel):
    id: uuid.UUID
    team_name: str
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    current_node_id: str
    path: list[str]
    total_score: int
    is_locked: bool
    lock_reason: str | None
    completed: bool
    moves: list[MoveOut]
    progress: list[ProgressOut]

    model_config = {"from_attributes": True}
