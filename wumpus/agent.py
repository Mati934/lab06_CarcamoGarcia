from __future__ import annotations

from typing import Optional

from . import search

Cell = tuple[int, int]

START: Cell = (0, 0)


class Agent:
    def __init__(self, environment, knowledge_base) -> None:
        self.environment = environment
        self.kb = knowledge_base

    def decide_next_action(self) -> Optional[str]:
        env = self.environment
        kb = self.kb
        pos: Cell = env.agent_pos

        if env.last_percept.glitter and not env.has_gold:
            return "grab"

        if env.has_gold:
            if pos == START:
                return "climb"
            path = search.find_path(pos, START, kb.known_safe_cells(), env.size)
            return path[0] if path else None

        return self._step_towards_nearest_unexplored(pos)

    def _step_towards_nearest_unexplored(self, pos: Cell) -> Optional[str]:
        env = self.environment
        kb = self.kb
        safe_cells = kb.known_safe_cells()
        targets = [c for c in safe_cells if c not in env.visited]

        best_path: Optional[list[str]] = None
        for target in targets:
            path = search.find_path(pos, target, safe_cells, env.size)
            if path is None:
                continue
            if best_path is None or len(path) < len(best_path):
                best_path = path

        return best_path[0] if best_path else None
