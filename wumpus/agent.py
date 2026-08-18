"""Agent: autonomous decision-making for the Wumpus World.

*** THIS FILE IS OWNED BY THE LOGIC/AGENT PAIR. ***

Contract expected by game.py (auto mode, triggered by SPACE):
    agent = Agent(environment, knowledge_base)
    action = agent.decide_next_action()   # called once per turn

`decide_next_action` must return one of:
    "up", "down", "left", "right", "grab", "climb",
    "shoot_up", "shoot_down", "shoot_left", "shoot_right"
or None if there is nothing safe to do yet (game.py will idle and show a
message rather than crash -- returning None is fine, just don't raise).

Guidance (rubric item 3):
  - Never return a move into a cell that `knowledge_base.infer_safe()` has
    not returned True for -- only move to demonstrated-safe cells.
  - Use search.find_path() to plan a route to the nearest unexplored safe
    cell, to the gold once its location is known (glitter percept), or
    back to (0, 0) to climb out once carrying gold.
  - Read the world only through `environment`'s percept/observation API
    (e.g. environment.last_percept, environment.cell_percepts,
    environment.visited, environment.agent_pos). Do not read
    environment.pits / .wumpus / .gold directly -- that would bypass the
    inference this lab is about.
"""
from __future__ import annotations

from typing import Optional


class Agent:
    def __init__(self, environment, knowledge_base) -> None:
        self.environment = environment
        self.kb = knowledge_base

    def decide_next_action(self) -> Optional[str]:
        raise NotImplementedError("TODO: implement autonomous decision-making")
