"""Small data-only structures shared between game.py and renderer.py.

Interface-owned. Not used by knowledge_base.py, agent.py or search.py.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CellView:
    visited: bool
    percept_glyph: str  # e.g. "~" breeze, "*" stench, "~*" both, "" none
    status: str  # "unknown" | "safe" | "pit" | "wumpus" | "gold"
    is_agent: bool


@dataclass
class HudInfo:
    cell: tuple[int, int]
    percepts: str
    score: int
    carrying: str
    arrows: int
    last_action: str
    mode: str
