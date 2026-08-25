"""Game loop: window, input handling, manual/auto modes, step-by-step.

Interface-owned. Wires together Environment (ground truth), KnowledgeBase +
Agent (owned by the logic pair) and Renderer (drawing) without ever
inspecting environment.pits/.wumpus/.gold itself -- only through the
percept API, exactly like the agent is supposed to.

Controls:
    arrows          move (manual mode)
    shift + arrows  shoot in that direction (manual mode)
    G               grab
    C               climb
    A               toggle manual / auto mode
    SPACE           one agent turn (auto mode only) -- the step-by-step
                    execution required by the rubric
    N               new cave (fresh random seed)
    R               restart (same seed, reproducible)
    ESC             quit
"""
from __future__ import annotations

import argparse
import random
from typing import Optional

import pygame

from . import config
from .agent import Agent
from .environment import MOVE_DELTA, Cell, Environment
from .knowledge_base import KnowledgeBase
from .renderer import Renderer
from .view_state import CellView, HudInfo

KEY_TO_DIRECTION = {
    pygame.K_UP: "up",
    pygame.K_DOWN: "down",
    pygame.K_LEFT: "left",
    pygame.K_RIGHT: "right",
}


def _safe_call(fn, *args, default=None):
    """Call a logic-pair method defensively: until knowledge_base.py /
    agent.py are implemented they raise NotImplementedError, and the
    interface should keep running (showing "?"/idling) rather than crash."""
    try:
        return fn(*args)
    except NotImplementedError:
        return default


def _inform_kb(env: Environment, kb: KnowledgeBase) -> None:
    cell = env.agent_pos
    percept = env.cell_percepts.get(cell)
    if percept is None:
        return
    try:
        # A visited cell only proves itself hazard-free if the agent is
        # still alive after entering it -- otherwise it may be the hazard.
        kb.tell_percept(cell, breeze=percept.breeze, stench=percept.stench, alive=env.alive)
    except NotImplementedError:
        pass


def _execute_action(env: Environment, action: str) -> None:
    if action in MOVE_DELTA:
        env.move(action)
    elif action == "grab":
        env.grab()
    elif action == "climb":
        env.climb()
    elif action.startswith("shoot_"):
        env.shoot(action.split("_", 1)[1])


def _agent_step(env: Environment, kb: KnowledgeBase, agent: Agent) -> None:
    action = _safe_call(agent.decide_next_action)
    if action is None:
        env.last_action = "agent: no action (not implemented yet, or nothing safe to do)"
        return
    _execute_action(env, action)
    _inform_kb(env, kb)


def _build_cell_views(env: Environment, kb: KnowledgeBase) -> list[list[CellView]]:
    grid: list[list[CellView]] = []
    for r in range(env.size):
        row: list[CellView] = []
        for c in range(env.size):
            cell: Cell = (c, r)
            visited = cell in env.visited
            percept = env.cell_percepts.get(cell)
            glyph = ""
            if percept is not None:
                if percept.breeze:
                    glyph += "~"
                if percept.stench:
                    glyph += "*"

            if visited and cell == env.gold and not env.has_gold:
                status = "gold"
            elif _safe_call(kb.infer_pit, cell):
                status = "pit"
            elif _safe_call(kb.infer_wumpus, cell):
                status = "wumpus"
            elif _safe_call(kb.infer_safe, cell):
                status = "safe"
            else:
                status = "unknown"

            if env.game_over and not env.alive and cell == env.agent_pos:
                if cell in env.pits:
                    status = "pit"
                elif cell in env.wumpus:
                    status = "wumpus"

            row.append(
                CellView(visited=visited, percept_glyph=glyph, status=status, is_agent=cell == env.agent_pos)
            )
        grid.append(row)
    return grid


def _build_hud(env: Environment, mode: str) -> HudInfo:
    last_action = env.last_action
    if env.game_over:
        last_action += "  [YOU WIN]" if env.won else "  [DEAD]"
    return HudInfo(
        cell=env.agent_pos,
        percepts=env.last_percept.describe(),
        score=env.score,
        carrying="gold" if env.has_gold else "nothing",
        arrows=env.arrows,
        last_action=last_action,
        mode=mode,
    )


def _new_episode(seed: Optional[int]) -> tuple[Environment, KnowledgeBase, Agent]:
    env = Environment(seed=seed)
    kb = KnowledgeBase(env.size)
    agent = Agent(env, kb)
    _inform_kb(env, kb)
    return env, kb, agent


def main() -> None:
    parser = argparse.ArgumentParser(description="Wumpus World lab")
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    args = parser.parse_args()

    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("Wumpus World")
    clock = pygame.time.Clock()
    renderer = Renderer(screen)

    env, kb, agent = _new_episode(args.seed)
    mode = "manual"
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_n:
                    env, kb, agent = _new_episode(random.SystemRandom().randint(0, 2**31 - 1))
                elif event.key == pygame.K_r:
                    env, kb, agent = _new_episode(env.seed)
                elif event.key == pygame.K_a:
                    mode = "auto" if mode == "manual" else "manual"
                elif event.key == pygame.K_SPACE:
                    if mode == "auto" and not env.is_terminal():
                        _agent_step(env, kb, agent)
                elif event.key == pygame.K_g and not env.is_terminal():
                    env.grab()
                elif event.key == pygame.K_c and not env.is_terminal():
                    env.climb()
                elif mode == "manual" and not env.is_terminal() and event.key in KEY_TO_DIRECTION:
                    direction = KEY_TO_DIRECTION[event.key]
                    if event.mod & pygame.KMOD_SHIFT:
                        env.shoot(direction)
                    else:
                        env.move(direction)
                        _inform_kb(env, kb)

        renderer.draw(_build_cell_views(env, kb), _build_hud(env, mode))
        clock.tick(config.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
