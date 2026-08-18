"""Search algorithm used by Agent to plan movement paths.

*** THIS FILE IS OWNED BY THE LOGIC/AGENT PAIR. ***

Suggested contract (adjust if needed, just keep agent.py in sync):
    path = find_path(start, goal, safe_cells, size)
    # path -> list of moves ("up"/"down"/"left"/"right") from `start` to
    #         `goal`, stepping only through cells in `safe_cells`
    #         (`start` itself does not need to be in `safe_cells`);
    #         or None if no such path exists.

Any complete, correct search algorithm satisfies rubric items 4 and 5 (BFS,
uniform-cost, A*, ...). Every move costs the same in this world, so BFS is
sufficient -- but feel free to use whatever you covered in class.

`agent.py` is expected to call this with `safe_cells = knowledge_base
.known_safe_cells()` so the agent only ever moves through cells the KB has
actually proven safe (rubric item 4).
"""
from __future__ import annotations

Cell = tuple[int, int]


def find_path(
    start: Cell,
    goal: Cell,
    safe_cells: set[Cell],
    size: int,
) -> list[str] | None:
    raise NotImplementedError("TODO: implement BFS/A* over safe_cells")
