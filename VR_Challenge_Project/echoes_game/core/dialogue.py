# core/dialogue.py
import pygame
from config import settings
from core import ui

class DialogueBox:
    def __init__(self, lines, on_finish=None):
        """
        lines: list[str]  ["Ryn: ...", "Lira: ..."]
        on_finish: callback بعد انتهاء الحوار
        """
        self.lines = lines
        self.index = 0
        self.on_finish = on_finish
        self.active = True
        self.margin = 40
        self.height = 120

    def handle_event(self, event):
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.index += 1
                if self.index >= len(self.lines):
                    self.active = False
                    if self.on_finish:
                        self.on_finish()

    def draw(self, surface):
        if not self.active:
            return

        panel_rect = pygame.Rect(
            self.margin,
            settings.HEIGHT - self.margin - self.height,
            settings.WIDTH - 2 * self.margin,
            self.height,
        )

        pygame.draw.rect(surface, settings.COLOR_PANEL, panel_rect, border_radius=10)
        pygame.draw.rect(surface, settings.COLOR_HIGHLIGHT, panel_rect, 2, border_radius=10)

        text = self.lines[self.index]
        words = text.split(" ")
        lines = []
        font = ui.get_font(22)
        max_width = panel_rect.width - 40

        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if font.size(test)[0] <= max_width:
                line = test
            else:
                lines.append(line)
                line = w
        if line:
            lines.append(line)

        y = panel_rect.y + 20
        for ln in lines:
            img = font.render(ln, True, settings.COLOR_TEXT)
            surface.blit(img, (panel_rect.x + 20, y))
            y += font.get_linesize() + 4

        hint_font = ui.get_font(16)
        hint_text = "[Space / Enter] التالي"
        img = hint_font.render(hint_text, True, settings.COLOR_HIGHLIGHT)
        surface.blit(img, (panel_rect.right - img.get_width() - 20,
                           panel_rect.bottom - img.get_height() - 10))
