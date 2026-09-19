from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_tables
from routers import admin, nodes, team, validate


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    title="NodeHunt 2026 API",
    description="Backend for NodeHunt 2026 — graph traversal, attempts, scoring, left/right movement, team tracking, and admin controls.",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(team.router)
app.include_router(nodes.router)
app.include_router(validate.router)
app.include_router(admin.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
