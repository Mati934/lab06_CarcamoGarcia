from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from . import config

Cell = tuple[int, int]


@dataclass
class _Percept:
    breeze: bool
    stench: bool


START: Cell = (0, 0)


class KnowledgeBase:
    def __init__(self, size: int) -> None:
        self.size = size
        self.visited: set[Cell] = set()
        self._percepts: dict[Cell, _Percept] = {}

        # Cells known hazard-free a priori: the start cell (a game-rule
        # guarantee) plus every cell the agent has visited AND survived.
        # A cell the agent died entering is deliberately *not* added here.
        self._confirmed_safe: set[Cell] = {START}
        # Cells known to hold at least one hazard: the agent died there.
        self._confirmed_hazard: set[Cell] = set()

        # Cached per tell_percept() call -- enumeration is only re-run once
        # new information actually arrives, since game.py queries the KB
        # every frame.
        self._model_cache: dict[str, list[dict[Cell, bool]]] = {}
        self._result_cache: dict[tuple[Cell, str], bool | None] = {}

    # ------------------------------------------------------------------ #
    # updating the KB
    # ------------------------------------------------------------------ #
    def tell_percept(self, cell: Cell, breeze: bool, stench: bool, alive: bool = True) -> None:
        """Record the percept obtained at `cell` and update the KB.

        `alive` must be False if this visit killed the agent -- otherwise
        the cell would be wrongly assumed hazard-free."""
        self.visited.add(cell)
        self._percepts[cell] = _Percept(breeze=breeze, stench=stench)
        if alive:
            self._confirmed_safe.add(cell)
        else:
            self._confirmed_hazard.add(cell)
        self._model_cache.clear()
        self._result_cache.clear()

    # ------------------------------------------------------------------ #
    # inference by enumeration
    # ------------------------------------------------------------------ #
    def infer_pit(self, cell: Cell) -> bool | None:
        if not self._in_bounds(cell):
            return None
        if cell in self._confirmed_safe:
            return False
        return self._enumerate_query(cell, "pit")

    def infer_wumpus(self, cell: Cell) -> bool | None:
        if not self._in_bounds(cell):
            return None
        if cell in self._confirmed_safe:
            return False
        return self._enumerate_query(cell, "wumpus")

    def infer_safe(self, cell: Cell) -> bool | None:
        if cell in self._confirmed_safe:
            return True
        if cell in self._confirmed_hazard:
            return False
        pit = self.infer_pit(cell)
        wumpus = self.infer_wumpus(cell)
        if pit is True or wumpus is True:
            return False
        if pit is False and wumpus is False:
            return True
        return None

    def known_safe_cells(self) -> set[Cell]:
        """All cells currently provable as safe -- used by search.py as the
        frontier the agent is allowed to path through."""
        safe = set(self._confirmed_safe)
        for cell in self._unknown_cells():
            if self.infer_safe(cell):
                safe.add(cell)
        return safe

    # ------------------------------------------------------------------ #
    # internals
    # ------------------------------------------------------------------ #
    def _in_bounds(self, cell: Cell) -> bool:
        c, r = cell
        return 0 <= c < self.size and 0 <= r < self.size

    def _neighbors(self, cell: Cell) -> list[Cell]:
        c, r = cell
        candidates = [(c, r - 1), (c, r + 1), (c - 1, r), (c + 1, r)]
        return [n for n in candidates if self._in_bounds(n)]

    def _unknown_cells(self) -> list[Cell]:
        """Every board cell not already known hazard-free -- the full set
        of unknowns once the total-hazard-count constraint (see
        `_satisfies`) is taken into account. This is deliberately wider
        than just the cells adjacent to a visited one: once a hazard's
        whole count is accounted for elsewhere, cells nowhere near any
        visited cell can become provably safe too."""
        all_cells = ((c, r) for r in range(self.size) for c in range(self.size))
        return sorted(cell for cell in all_cells if cell not in self._confirmed_safe)

    def _enumerate_query(self, cell: Cell, kind: str) -> bool | None:
        cache_key = (cell, kind)
        if cache_key in self._result_cache:
            return self._result_cache[cache_key]

        unknowns = self._unknown_cells()
        models = self._consistent_models(kind, unknowns)
        if not models:
            # Should not happen with a consistent world, but fail safe.
            result = None
        elif all(model[cell] for model in models):
            result = True
        elif all(not model[cell] for model in models):
            result = False
        else:
            result = None

        self._result_cache[cache_key] = result
        return result

    def _consistent_models(self, kind: str, unknowns: list[Cell]) -> list[dict[Cell, bool]]:
        if kind in self._model_cache:
            return self._model_cache[kind]

        models: list[dict[Cell, bool]] = []
        for bits in product((False, True), repeat=len(unknowns)):
            assignment = dict(zip(unknowns, bits))
            if self._satisfies(assignment, kind):
                models.append(assignment)

        self._model_cache[kind] = models
        return models

    def _satisfies(self, assignment: dict[Cell, bool], kind: str) -> bool:
        """Check `assignment` (True = danger present at that unknown cell)
        against every observed breeze_v <=> OR(neighbors) / stench_v <=>
        OR(neighbors) clause, plus the known total count of that hazard
        (a game-rule guarantee, same spirit as START always being safe).
        Cells outside `assignment` are implicitly False -- by construction
        (see `_unknown_cells`) those are exactly the cells already in
        `_confirmed_safe`."""
        total_target = config.NUM_PITS if kind == "pit" else config.NUM_WUMPUS
        if sum(assignment.values()) != total_target:
            return False

        for v in self.visited:
            percept = self._percepts.get(v)
            if percept is None:
                continue
            observed = percept.breeze if kind == "pit" else percept.stench
            computed = any(assignment.get(n, False) for n in self._neighbors(v))
            if computed != observed:
                return False
        return True
