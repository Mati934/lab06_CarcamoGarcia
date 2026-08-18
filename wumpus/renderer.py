"""Pure rendering layer -- draws the grid + console HUD with PyGame.

Interface-owned. Nothing here touches game rules or inference; it only
turns already-computed CellView/HudInfo data (built in game.py) into
pixels. Keeping draw code isolated here means the logic/agent pair can
change knowledge_base.py, agent.py and search.py freely without ever
touching this file, and vice versa.
"""
from __future__ import annotations

import pygame

from . import config
from .view_state import CellView, HudInfo

CONTROLS_LINES = [
    "arrows move   G grab   C climb",
    "shift+arrow shoot   A auto   SPACE one turn",
    "N new cave   R restart   ESC quit",
]

_CELL_LABELS = {
    "pit": "P!",
    "wumpus": "W!",
    "safe": "OK",
    "gold": "AU",
}


class Renderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        pygame.font.init()
        self.font_cell = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_glyph = pygame.font.SysFont("consolas", 14)
        self.font_hud = pygame.font.SysFont("consolas", 16)

    def draw(self, grid: list[list[CellView]], hud: HudInfo) -> None:
        self.screen.fill(config.COLOR_BG)
        self._draw_grid(grid)
        self._draw_console(hud)
        pygame.display.flip()

    def _draw_grid(self, grid: list[list[CellView]]) -> None:
        for row_idx, row in enumerate(grid):
            for col_idx, cell in enumerate(row):
                x = col_idx * config.CELL_PX
                y = row_idx * config.CELL_PX
                rect = pygame.Rect(x, y, config.CELL_PX, config.CELL_PX)

                pygame.draw.rect(self.screen, self._cell_color(cell), rect)
                pygame.draw.rect(self.screen, config.COLOR_GRID_LINE, rect, width=1)

                if cell.percept_glyph:
                    glyph_surf = self.font_glyph.render(cell.percept_glyph, True, config.COLOR_TEXT_DIM)
                    self.screen.blit(glyph_surf, (x + 6, y + 4))

                label = "" if cell.is_agent else _CELL_LABELS.get(cell.status, "")
                if label:
                    label_surf = self.font_cell.render(label, True, config.COLOR_TEXT)
                    self.screen.blit(label_surf, label_surf.get_rect(center=rect.center))

                if cell.is_agent:
                    pygame.draw.circle(self.screen, config.COLOR_AGENT, rect.center, config.CELL_PX // 5)

    def _cell_color(self, cell: CellView) -> tuple[int, int, int]:
        if cell.status in ("pit", "wumpus"):
            return config.COLOR_CELL_DANGER
        if cell.status == "safe":
            return config.COLOR_CELL_SAFE
        if cell.status == "gold":
            return config.COLOR_CELL_GOLD
        if cell.visited:
            return config.COLOR_CELL_VISITED
        return config.COLOR_CELL_UNKNOWN

    def _draw_console(self, hud: HudInfo) -> None:
        top = config.GRID_SIZE * config.CELL_PX
        rect = pygame.Rect(0, top, config.WINDOW_WIDTH, config.CONSOLE_HEIGHT)
        pygame.draw.rect(self.screen, config.COLOR_CONSOLE_BG, rect)

        info_lines = [
            f"cell {hud.cell}   perceives: {hud.percepts}",
            f"score {hud.score}   carrying {hud.carrying}   arrows {hud.arrows}",
            f"last action {hud.last_action}   mode {hud.mode}",
        ]
        for i, line in enumerate(info_lines):
            surf = self.font_hud.render(line, True, config.COLOR_TEXT)
            self.screen.blit(surf, (10, top + 8 + i * 18))

        gap = 8
        for i, line in enumerate(CONTROLS_LINES):
            surf = self.font_hud.render(line, True, config.COLOR_TEXT_DIM)
            self.screen.blit(surf, (10, top + 8 + len(info_lines) * 18 + gap + i * 18))
