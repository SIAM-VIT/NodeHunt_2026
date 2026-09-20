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
        "difficulty": "medium",
        "is_start": True,
        "is_terminal": False,
        "question": {
            "set1": "Challenge Node N01 (Debugging): Analyze the provided code, trace edge cases, and resolve the defect.",
        },
        "answers": ["nodehunt", "verified26", "solved", "sunsunsunday", "siamvit"],
        "routes": {"left": "N02", "right": "N03"},
    },
    "N02": {
        "type": "C",
        "difficulty": "easy",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Challenge Node N02 (Coding): Implement the optimal algorithmic solution with minimal complexity."},
        "answers": ["nodehunt", "verified26", "solved", "sunsunsunday", "siamvit"],
        "routes": {"left": "N04", "right": "N03"},
    },
    "N03": {
        "type": "R",
        "difficulty": "medium",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Challenge Node N03 (Riddle): Deduce the logic enigma and unlock the solution passcode."},
        "answers": ["nodehunt", "verified26", "solved", "sunsunsunday", "siamvit"],
        "routes": {"left": "N05", "right": "N06"},
    },
    "N04": {
        "type": "Q",
        "difficulty": "hard",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Challenge Node N04 (Quiz): Answer the systems & networking architectural theory question."},
        "answers": ["nodehunt", "verified26", "solved", "sunsunsunday", "siamvit"],
        "routes": {"left": "N07", "right": "N06"},
    },
    "N05": {
        "type": "C",
        "difficulty": "medium",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Challenge Node N05 (Coding): Implement data structure manipulation under tight constraints."},
        "answers": ["nodehunt", "verified26", "solved", "sunsunsunday", "siamvit"],
        "routes": {"left": "N08", "right": "N09"},
    },
    "N06": {
        "type": "D",
        "difficulty": "medium",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Challenge Node N06 (Debugging): Inspect the concurrent execution logs and patch the race condition."},
        "answers": ["nodehunt", "verified26", "solved", "sunsunsunday", "siamvit"],
        "routes": {"left": "N05", "right": "N10"},
    },
    "N07": {
        "type": "D",
        "difficulty": "easy",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Challenge Node N07 (Debugging): Find the off-by-one boundary error in the traversal loop."},
        "answers": ["nodehunt", "verified26", "solved", "sunsunsunday", "siamvit"],
        "routes": {"continue": "N09", "left": "N09", "right": "N09"},
    },
    "N08": {
        "type": "Q",
        "difficulty": "hard",
        "is_start": False,
        "is_terminal": True,
        "question": {"set1": "Final Tournament Objective Node N08 (Grand Finale): What is the chromatic number of the Petersen graph?"},
        "answers": ["nodehunt", "verified26", "solved", "sunsunsunday", "siamvit", "3"],
        "routes": {},
    },
    "N09": {
        "type": "R",
        "difficulty": "medium",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Challenge Node N09 (Riddle): Crack the algorithmic cipher to progress toward the finale."},
        "answers": ["nodehunt", "verified26", "solved", "sunsunsunday", "siamvit"],
        "routes": {"continue": "N08", "left": "N08", "right": "N08"},
    },
    "N10": {
        "type": "C",
        "difficulty": "easy",
        "is_start": False,
        "is_terminal": False,
        "question": {"set1": "Challenge Node N10 (Coding): Implement optimal substring search and hash table lookup."},
        "answers": ["nodehunt", "verified26", "solved", "sunsunsunday", "siamvit"],
        "routes": {"continue": "N09", "left": "N09", "right": "N09"},
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
