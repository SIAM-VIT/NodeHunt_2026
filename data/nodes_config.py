"""
NodeHunt 2026 graph configuration.

This keeps the old backend philosophy: graph, questions, and accepted answers are
centralized server-side. The frontend never receives answers.

New 2026 behavior:
- `answers` validate the current node only.
- `routes.left/right` decide movement after solve/exhaustion.
- terminal nodes complete the hunt after validation or exhaustion.
"""

from typing import Any

SCORE_BY_ATTEMPT: dict[int, int] = {
    1: 30,
    2: 20,
    3: 10,
}

MAX_ATTEMPTS = 3
START_NODE_ID = "N01"

NODES: dict[str, dict[str, Any]] = {
    "N01": {
        "type": "D",
        "difficulty": "easy",
        "is_start": True,
        "is_terminal": False,
        "question": {
            "set1": "Demo Debugging Node N01. Replace this with the real debugging question.",
        },
        "answers": ["nodehunt"],
        "routes": {"left": "N02", "right": "N03"},
    },
    "N02": {
        "type": "R",
        "difficulty": "hard",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Demo Riddle Node N02. Replace with real question."},
        "answers": ["nodehunt"],
        "routes": {"left": "N04", "right": "N05"},
    },
    "N03": {
        "type": "Q",
        "difficulty": "medium",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Demo Quiz Node N03. Replace with real question."},
        "answers": ["nodehunt"],
        "routes": {"left": "N05", "right": "N06"},
    },
    "N04": {
        "type": "C",
        "difficulty": "medium",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Demo Coding Node N04. Replace with real question."},
        "answers": ["nodehunt"],
        "routes": {"left": "N07", "right": "N08"},
    },
    "N05": {
        "type": "C",
        "difficulty": "easy",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Demo Coding Node N05. Replace with real question."},
        "answers": ["nodehunt"],
        "routes": {"left": "N08", "right": "N09"},
    },
    "N06": {
        "type": "C",
        "difficulty": "hard",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Demo Coding Node N06. Replace with real question."},
        "answers": ["nodehunt"],
        "routes": {"left": "N09", "right": "N10"},
    },
    "N07": {
        "type": "R",
        "difficulty": "easy",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Demo Riddle Node N07. Replace with real question."},
        "answers": ["nodehunt"],
        "routes": {"left": "N14", "right": "N11"},
    },
    "N08": {
        "type": "Q",
        "difficulty": "hard",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Demo Quiz Node N08. Replace with real question."},
        "answers": ["nodehunt"],
        "routes": {"left": "N11", "right": "N12"},
    },
    "N09": {
        "type": "D",
        "difficulty": "medium",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Demo Debugging Node N09. Replace with real question."},
        "answers": ["nodehunt"],
        "routes": {"left": "N12", "right": "N13"},
    },
    "N10": {
        "type": "R",
        "difficulty": "easy",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Demo Riddle Node N10. Replace with real question."},
        "answers": ["nodehunt"],
        "routes": {"left": "N13", "right": "N14"},
    },
    "N11": {
        "type": "D",
        "difficulty": "medium",
        "is_start": False,
        "is_terminal": True,
        "question": {"set1": "Final Debugging Node N11. Replace with real final question."},
        "answers": ["nodehunt"],
        "routes": {},
    },
    "N12": {
        "type": "R",
        "difficulty": "easy",
        "is_start": False,
        "is_terminal": True,
        "question": {"set1": "Final Riddle Node N12. Replace with real final question."},
        "answers": ["nodehunt"],
        "routes": {},
    },
    "N13": {
        "type": "C",
        "difficulty": "medium",
        "is_start": False,
        "is_terminal": True,
        "question": {"set1": "Final Coding Node N13. Replace with real final question."},
        "answers": ["nodehunt"],
        "routes": {},
    },
    "N14": {
        "type": "Q",
        "difficulty": "hard",
        "is_start": False,
        "is_terminal": True,
        "question": {"set1": "Shared Final Quiz Node N14. Replace with real final question."},
        "answers": ["nodehunt"],
        "routes": {},
    },
}

NODE_NUMBERS: dict[str, int] = {node_id: index for index, node_id in enumerate(NODES, start=1)}


def normalize_answer(value: str) -> str:
    """Simple accepted-answer normalization for MVP/event use."""
    return " ".join(value.strip().lower().split())


def is_correct_answer(node_id: str, answer: str) -> bool:
    node = NODES.get(node_id)
    if not node:
        return False
    normalized = normalize_answer(answer)
    return normalized in {normalize_answer(item) for item in node.get("answers", [])}


def get_available_routes(node_id: str) -> list[dict[str, str | bool]]:
    node = NODES[node_id]
    route_previews: list[dict[str, str | bool]] = []
    for direction, target_id in node.get("routes", {}).items():
        target = NODES[target_id]
        route_previews.append(
            {
                "direction": direction,
                "type": target["type"],
                "difficulty": target["difficulty"],
                "terminal": bool(target.get("is_terminal", False)),
            }
        )
    return route_previews
