from __future__ import annotations

from collections import deque

Cell = tuple[int, int]

_DIRECTIONS: dict[str, Cell] = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}


def find_path(
    start: Cell,
    goal: Cell,
    safe_cells: set[Cell],
    size: int,
) -> list[str] | None:
    if start == goal:
        return []

    visited: set[Cell] = {start}
    queue: deque[tuple[Cell, list[str]]] = deque([(start, [])])

    while queue:
        cell, path = queue.popleft()
        for direction, (dc, dr) in _DIRECTIONS.items():
            nxt: Cell = (cell[0] + dc, cell[1] + dr)

            if not (0 <= nxt[0] < size and 0 <= nxt[1] < size):
                continue
            if nxt in visited or nxt not in safe_cells:
                continue

            new_path = path + [direction]
            if nxt == goal:
                return new_path

            visited.add(nxt)
            queue.append((nxt, new_path))

    return None
