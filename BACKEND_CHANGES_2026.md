# NodeHunt 2026 Backend Additions

This backend keeps the original FastAPI/PostgreSQL/router style but adds the small game-logic extensions needed for the 2026 event.

## Added gameplay behavior

- Team name/password creation and editing before game start.
- Admin can edit team names anytime.
- Admin can lock/unlock teams.
- Per-node attempt tracking.
- Attempt-based scoring:
  - attempt 1 = 30
  - attempt 2 = 20
  - attempt 3 = 10
  - all wrong = 0
- After 3 wrong attempts, movement unlocks by default.
- Correct answers unlock movement.
- Answer validation is separated from movement.
- Movement now happens through `POST /api/move` with `left` or `right`.
- Terminal nodes complete the hunt after correct answer or after 3 wrong attempts.

## Important files

```text
main.py
config.py
database.py
models.py
schemas.py
data/nodes_config.py
routers/team.py
routers/nodes.py
routers/validate.py
routers/admin.py
routers/utils.py
```

## New/updated models

### Team

Added:

```text
team_name
started_at
completed_at
total_score
is_locked
lock_reason
completed
path as JSONB list of node IDs
```

### TeamNodeProgress

New table:

```text
team_id
node_id
attempts_used
solved
exhausted
movement_unlocked
points_awarded
solved_at
```

### TeamMove

Now stores:

```text
from_node
to_node
direction
moved_at
```

## API summary

### Create team

```http
POST /api/team
```

```json
{
  "team_name": "Stack Hunters",
  "password": "team-password"
}
```

### Start team

```http
POST /api/team/start
```

```json
{
  "session_id": "uuid"
}
```

### User edit team name before start

```http
PATCH /api/team/name
```

```json
{
  "session_id": "uuid",
  "team_name": "New Name"
}
```

### Fetch current node

```http
GET /api/node/N01?session_id=uuid
```

### Validate answer

```http
POST /api/validate
```

```json
{
  "session_id": "uuid",
  "node_id": "N01",
  "answer": "nodehunt"
}
```

Correct answer unlocks movement and returns available route previews.

### Move after unlock

```http
POST /api/move
```

```json
{
  "session_id": "uuid",
  "node_id": "N01",
  "direction": "left"
}
```

### Admin teams

```http
GET /api/admin/teams
x-admin-secret: changeme
```

### Admin lock/unlock

```http
PATCH /api/admin/team/{team_id}/lock
x-admin-secret: changeme
```

```json
{
  "locked": true,
  "reason": "Rule violation"
}
```

### Admin edit team name

```http
PATCH /api/admin/team/{team_id}/name
x-admin-secret: changeme
```

```json
{
  "team_name": "Updated Name"
}
```

## Graph config

The confirmed graph is in:

```text
data/nodes_config.py
```

Current questions and answers are placeholders. Replace:

```python
"question": {...}
"answers": [...]
```

with real event content.

For demos, every node currently accepts:

```text
nodehunt
```

## Notes for senior backend owner

This is intentionally not a full backend rewrite.

It preserves the original style:

- FastAPI routers
- centralized `nodes_config.py`
- SQLAlchemy async models
- simple admin secret
- table creation on startup

Recommended production improvements later:

- Alembic migrations
- stricter CORS
- Redis rate limiting if needed
- JWT/admin login instead of shared secret
- move questions into DB/admin dashboard later
