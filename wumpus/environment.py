"""Wumpus World environment: grid generation and game-mechanics rules.

Interface-owned (not the logic/agent pair's file).

This module owns the *ground truth* of the cave (pit/wumpus/gold locations,
percepts, scoring, death/win conditions) and exposes a small action API. It
intentionally knows nothing about inference, search or agent strategy --
that lives in knowledge_base.py, search.py and agent.py.

Coordinates are (col, row) with (0, 0) at the top-left, matching how the
grid is drawn on screen. "up" decreases row, "down" increases row, "left"
decreases col, "right" increases col.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from . import config

Cell = tuple[int, int]

MOVE_DELTA: dict[str, Cell] = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}


@dataclass
class Percept:
    breeze: bool = False
    stench: bool = False
    glitter: bool = False
    bump: bool = False
    scream: bool = False

    def describe(self) -> str:
        flags = [
            name
            for name, val in (
                ("breeze", self.breeze),
                ("stench", self.stench),
                ("glitter", self.glitter),
                ("bump", self.bump),
                ("scream", self.scream),
            )
            if val
        ]
        return ", ".join(flags) if flags else "nothing"


class Environment:
    """Ground-truth Wumpus World state and mechanics (not the agent's beliefs)."""

    def __init__(
        self,
        size: int = config.GRID_SIZE,
        seed: int | None = None,
        num_pits: int = config.NUM_PITS,
        num_wumpus: int = config.NUM_WUMPUS,
    ) -> None:
        self.size = size
        self.num_pits = num_pits
        self.num_wumpus = num_wumpus
        self.reset(seed if seed is not None else config.DEFAULT_SEED)

    # ------------------------------------------------------------------ #
    # world generation
    # ------------------------------------------------------------------ #
    def reset(self, seed: int | None = None) -> None:
        """Regenerate the cave deterministically from `seed` (reproducible)."""
        if seed is not None:
            self.seed = seed
        rng = random.Random(self.seed)

        start: Cell = (0, 0)
        all_cells = [(c, r) for r in range(self.size) for c in range(self.size)]
        candidates = [c for c in all_cells if c != start]

        self.pits: set[Cell] = set(rng.sample(candidates, k=min(self.num_pits, len(candidates))))
        remaining = [c for c in candidates if c not in self.pits]
        self.wumpus: set[Cell] = set(rng.sample(remaining, k=min(self.num_wumpus, len(remaining))))
        remaining = [c for c in remaining if c not in self.wumpus]
        self.gold: Cell = rng.choice(remaining) if remaining else rng.choice(candidates)

        self.agent_pos: Cell = start
        self.alive = True
        self.has_gold = False
        self.game_over = False
        self.won = False
        self.arrows = 1
        self.score = 0
        self.visited: set[Cell] = {start}
        self.last_action: str = "none"
        self.last_percept = self.percept_at(start)
        self.cell_percepts: dict[Cell, Percept] = {start: self.last_percept}

    # ------------------------------------------------------------------ #
    # queries
    # ------------------------------------------------------------------ #
    def in_bounds(self, cell: Cell) -> bool:
        c, r = cell
        return 0 <= c < self.size and 0 <= r < self.size

    def neighbors(self, cell: Cell) -> list[Cell]:
        c, r = cell
        candidates = [(c, r - 1), (c, r + 1), (c - 1, r), (c + 1, r)]
        return [n for n in candidates if self.in_bounds(n)]

    def percept_at(self, cell: Cell) -> Percept:
        breeze = any(n in self.pits for n in self.neighbors(cell))
        stench = any(n in self.wumpus for n in self.neighbors(cell))
        glitter = cell == self.gold and not self.has_gold
        return Percept(breeze=breeze, stench=stench, glitter=glitter)

    def is_terminal(self) -> bool:
        return self.game_over

    # ------------------------------------------------------------------ #
    # actions -- each costs points per the classic Wumpus World scoring and
    # returns the resulting Percept so callers/UI can react to it.
    # ------------------------------------------------------------------ #
    def move(self, direction: str) -> Percept:
        if self.game_over:
            return self.last_percept

        dx, dy = MOVE_DELTA[direction]
        target = (self.agent_pos[0] + dx, self.agent_pos[1] + dy)
        self.score -= 1
        self.last_action = f"move {direction}"

        if not self.in_bounds(target):
            self.last_percept = self.percept_at(self.agent_pos)
            self.last_percept.bump = True
            return self.last_percept

        self.agent_pos = target
        self.visited.add(target)

        if target in self.pits or target in self.wumpus:
            self.alive = False
            self.game_over = True
            self.score -= 1000

        self.last_percept = self.percept_at(target)
        self.cell_percepts[target] = self.last_percept
        return self.last_percept

    def grab(self) -> Percept:
        self.last_action = "grab"
        self.score -= 1
        if self.agent_pos == self.gold and not self.has_gold:
            self.has_gold = True
            self.score += 10
        self.last_percept = self.percept_at(self.agent_pos)
        return self.last_percept

    def shoot(self, direction: str) -> Percept:
        self.last_action = f"shoot {direction}"
        self.last_percept = self.percept_at(self.agent_pos)
        if self.arrows > 0:
            self.arrows -= 1
            self.score -= 10
            dx, dy = MOVE_DELTA[direction]
            c, r = self.agent_pos
            c, r = c + dx, r + dy
            path: list[Cell] = []
            while self.in_bounds((c, r)):
                path.append((c, r))
                c, r = c + dx, r + dy
            hit = next((cell for cell in path if cell in self.wumpus), None)
            if hit is not None:
                self.wumpus.discard(hit)
                self.last_percept.scream = True
        return self.last_percept

    def climb(self) -> Percept:
        self.last_action = "climb"
        self.score -= 1
        if self.agent_pos == (0, 0):
            self.game_over = True
            self.won = self.has_gold
            if self.has_gold:
                self.score += 1000
        self.last_percept = self.percept_at(self.agent_pos)
        return self.last_percept
