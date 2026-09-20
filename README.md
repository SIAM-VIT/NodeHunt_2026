# NodeHunt 2026 — Backend API Server

High-performance, asynchronous REST API engine powering **NodeHunt 2026**, built with **FastAPI**, **SQLAlchemy (Async)**, and **SQLite/PostgreSQL**.

---

## Overview & Architecture

NodeHunt is a competitive graph-traversal coding hunt designed for SIAM-VIT. The backend orchestrates session states, validates invigilator verification attempts, manages attempt-based point allocation, enforces topological Fog-of-War graph traversal, and delivers real-time telemetry to the admin dashboard.

### Core Features

- **Asynchronous Architecture**: Built on FastAPI and Starlette with high concurrency support.
- **Topological Graph Traversal**: Enforces strict node-to-node path traversal across the tournament graph with branching routes (`left`, `right`, `continue`).
- **Attempt-Based Scoring**:
  - 1st attempt solve: **30 PTS**
  - 2nd attempt solve: **20 PTS**
  - 3rd attempt solve: **10 PTS**
  - All 3 attempts exhausted: **0 PTS**, with forward path unlocked to guarantee team progression.
- **Invigilator Verification Model**: Solution approval and retry recording decoupled from participant inputs.
- **Organizer Telemetry**: Live admin controls, team locking/unlocking, team renaming, and tournament state resets.
- **Tournament Standings Engine**: Live leaderboard ranking completed teams by highest score and earliest completion time.

---

## System Requirements

- **Python**: 3.10, 3.11, 3.12, or 3.13
- **Git**
- **Virtual Environment tool** (`venv` or `conda`)

---

## Installation & Setup Guide

### Windows Setup (PowerShell / Command Prompt)

1. **Clone the Repository**:
   ```powershell
   git clone https://github.com/harshtiwari0225-commits/nodehunt-2026.git
   cd nodehunt-2026
   ```

2. **Create a Virtual Environment**:
   ```powershell
   python -m venv venv
   ```

3. **Activate the Virtual Environment**:
   - In PowerShell:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
     *(If script execution is disabled on your system, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*
   - In Command Prompt:
     ```cmd
     .\venv\Scripts\activate.bat
     ```

4. **Install Dependencies**:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Environment Configuration**:
   Create a `.env` file in the project root:
   ```env
   DATABASE_URL=sqlite+aiosqlite:///./nodehunt.db
   ADMIN_SECRET=your_admin_secret_key_here
   ```

6. **Start the API Server**:
   ```powershell
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   The backend will be live at `http://localhost:8000`.  
   Interactive API documentation (Swagger UI) is available at `http://localhost:8000/docs`.

---

### macOS & Linux Setup

1. **Clone and Enter Repository**:
   ```bash
   git clone https://github.com/harshtiwari0225-commits/nodehunt-2026.git
   cd nodehunt-2026
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Run Server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

---

## Directory Structure

```text
├── config.py              # Application configuration & environment settings
├── database.py            # Async engine and database session lifecycle
├── main.py                # FastAPI entry point, CORS, and router registration
├── models.py              # SQLAlchemy ORM schemas (Teams, Moves, Node Progress)
├── schemas.py             # Pydantic request and response models
├── requirements.txt       # Python package dependencies
├── data/
│   └── nodes_config.py    # Topological node relationships and routing rules
└── routers/
    ├── admin.py           # Organizer endpoints, team controls, and leaderboard
    ├── nodes.py           # Current node retrieval and progress serialization
    ├── team.py            # Team session authentication and lifecycle
    ├── utils.py           # Common validation and scoring helpers
    └── validate.py        # Verification state machine and move transitions
```

---

## API Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/team` | Provision a new team session |
| `POST` | `/api/team/login` | Authenticate team credentials |
| `POST` | `/api/team/start` | Initialize team traversal at node N01 |
| `GET` | `/api/node/{node_id}` | Fetch challenge details and route previews for active node |
| `POST` | `/api/validate` | Process invigilator verification or retry strike |
| `POST` | `/api/move` | Execute left, right, or continue branch traversal |
| `GET` | `/api/leaderboard` | Retrieve official tournament standings |
| `GET` | `/api/team/{id}/result`| Get personalized team scorecard and path audit |
| `GET` | `/api/admin/teams` | Organizer live telemetry and team rosters |
| `PATCH` | `/api/admin/team/{id}/lock` | Admin lock or unlock team progression |
| `DELETE`| `/api/admin/teams` | Emergency wipe of tournament state |
