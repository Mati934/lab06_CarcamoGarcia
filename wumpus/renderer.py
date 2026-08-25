"""Pure rendering layer -- draws the grid + console HUD with PyGame.

Interface-owned. Nothing here touches game rules or inference; it only
turns already-computed CellView/HudInfo data (built in game.py) into
pixels. Keeping draw code isolated here means the logic/agent pair can
change knowledge_base.py, agent.py and search.py freely without ever
touching this file, and vice versa.
"""
from __future__ import annotations

from pathlib import Path

import pygame

from . import config
from .view_state import CellView, HudInfo

CONTROLS_LINES = [
    "arrows move   G grab   C climb",
    "shift+arrow shoot   A auto   SPACE one turn",
    "N new cave   R restart   ESC quit",
]

_CELL_LABELS = {
    "safe": "OK",
}

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

# Full-cell background tiles, drawn first (grass everywhere, well.png
# replacing it on pit cells) -- both stretched to fill the whole cell.
_TILE_FILES = {
    "floor": "grass.png",
    "pit": "well.png",
}

# Smaller icons centered on top of the tile: the agent marker, the
# wumpus/gold cell statuses, and the gold badge overlaid on the agent when
# it's standing on the (not yet grabbed) gold cell.
_ICON_FILES = {
    "agent": "steeve.png",
    "wumpus": "wumpus.png",
    "gold": "gold.png",
    "gold_badge": "gold.png",
}

_TINT_ALPHA = 90  # status color drawn translucent over the grass/well tile


class Renderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        pygame.font.init()
        self.font_cell = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_glyph = pygame.font.SysFont("consolas", 14)
        self.font_hud = pygame.font.SysFont("consolas", 16)
        self.tiles = self._load_scaled(_TILE_FILES, (config.CELL_PX, config.CELL_PX))
        self.icons = self._load_scaled(_ICON_FILES, (config.CELL_PX - 24, config.CELL_PX - 24))
        self.icons["gold_badge"] = pygame.transform.smoothscale(
            self.icons["gold_badge"],
            (round(self.icons["gold_badge"].get_width() * 0.55), round(self.icons["gold_badge"].get_height() * 0.55)),
        )

    def _load_scaled(self, files: dict[str, str], max_size: tuple[int, int]) -> dict[str, pygame.Surface]:
        max_w, max_h = max_size
        sprites: dict[str, pygame.Surface] = {}
        for key, filename in files.items():
            path = ASSETS_DIR / filename
            image = pygame.image.load(str(path))
            if not image.get_flags() & pygame.SRCALPHA:
                # No per-pixel alpha in this asset (opaque background) --
                # key out its corner color so it blends with the cell color
                # like the other sprites instead of showing a solid square.
                image.set_colorkey(image.get_at((0, 0)))
            image = image.convert_alpha()
            scale = min(max_w / image.get_width(), max_h / image.get_height())
            size = (max(1, round(image.get_width() * scale)), max(1, round(image.get_height() * scale)))
            sprites[key] = pygame.transform.smoothscale(image, size)
        return sprites

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

                # 1. ground tile -- well.png on a confirmed pit, grass.png
                #    everywhere else, both filling the whole cell.
                tile = self.tiles["pit"] if cell.status == "pit" else self.tiles["floor"]
                self.screen.blit(tile, (x, y))

                # 2. translucent status tint on top of the tile, so safe /
                #    unknown / danger cells stay readable at a glance.
                tint = pygame.Surface((config.CELL_PX, config.CELL_PX), pygame.SRCALPHA)
                tint.fill((*self._cell_color(cell), _TINT_ALPHA))
                self.screen.blit(tint, (x, y))

                pygame.draw.rect(self.screen, config.COLOR_GRID_LINE, rect, width=1)

                if cell.percept_glyph:
                    glyph_surf = self.font_glyph.render(cell.percept_glyph, True, config.COLOR_TEXT_DIM)
                    self.screen.blit(glyph_surf, (x + 6, y + 4))

                # 3. character/creature icon on top of the tile+tint.
                icon_key = "agent" if cell.is_agent else cell.status
                icon = self.icons.get(icon_key)
                if icon is not None:
                    self.screen.blit(icon, icon.get_rect(center=rect.center))
                else:
                    label = _CELL_LABELS.get(cell.status, "")
                    if label:
                        label_surf = self.font_cell.render(label, True, config.COLOR_TEXT)
                        self.screen.blit(label_surf, label_surf.get_rect(center=rect.center))

                # 4. gold badge overlaid on the agent so finding the gold is
                #    still visible even though the agent icon covers the
                #    cell (rubric: the game must show discoveries clearly).
                if cell.is_agent and cell.status == "gold":
                    badge = self.icons["gold_badge"]
                    badge_rect = badge.get_rect()
                    badge_rect.bottomright = (rect.right - 6, rect.bottom - 6)
                    self.screen.blit(badge, badge_rect)

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
