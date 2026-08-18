"""KnowledgeBase: propositional rules for the Wumpus World + inference.

*** THIS FILE IS OWNED BY THE LOGIC/AGENT PAIR. ***
game.py, renderer.py, view_state.py and environment.py belong to the
interface pair and should not need to change while you work here -- and
this file should not need to touch pygame at all.

Required behaviour (rubric items 2 and 4):
  - Encode breeze/stench rules for every visited cell as logical clauses,
    e.g. B_(x,y) <=> P_(x-1,y) v P_(x+1,y) v P_(x,y-1) v P_(x,y+1), and the
    equivalent S_(x,y) <=> W_... clause for the Wumpus.
  - Provide inference **by enumeration** (or an equivalent complete method,
    per the lab objectives) that can PROVE a cell is safe (no pit AND no
    wumpus), or PROVE it is dangerous, from the percepts accumulated so
    far. A cell that cannot be proven either way must stay unknown --
    never guess.

Contract expected by game.py (see `_inform_kb` and `_build_cell_views`):
    kb = KnowledgeBase(size)
    kb.tell_percept(cell, breeze=bool, stench=bool)   # after visiting `cell`
    kb.infer_safe(cell)    -> True / False / None
    kb.infer_pit(cell)     -> True / False / None
    kb.infer_wumpus(cell)  -> True / False / None
    kb.known_safe_cells()  -> set[tuple[int, int]]

`None` always means "not yet provable" -- game.py shows "?" for that, and
agent.py/search.py must never treat `None` as safe.

Until these methods are implemented, game.py catches the NotImplementedError
below and treats every query as unknown, so the interface stays runnable
(showing "?" everywhere) while you build this out.
"""
from __future__ import annotations

Cell = tuple[int, int]


class KnowledgeBase:
    def __init__(self, size: int) -> None:
        self.size = size
        # TODO: set up your clause storage / symbols here.

    def tell_percept(self, cell: Cell, breeze: bool, stench: bool) -> None:
        """Record the percept obtained at `cell` and update the KB."""
        raise NotImplementedError("TODO: implement KB update from percepts")

    def infer_safe(self, cell: Cell) -> bool | None:
        """True if `cell` is provably free of pit and wumpus, False if
        provably dangerous, None if not yet provable either way."""
        raise NotImplementedError("TODO: implement inference by enumeration")

    def infer_pit(self, cell: Cell) -> bool | None:
        raise NotImplementedError("TODO: implement inference by enumeration")

    def infer_wumpus(self, cell: Cell) -> bool | None:
        raise NotImplementedError("TODO: implement inference by enumeration")

    def known_safe_cells(self) -> set[Cell]:
        """All cells currently provable as safe -- used by search.py as the
        frontier the agent is allowed to path through."""
        raise NotImplementedError("TODO: implement inference by enumeration")
