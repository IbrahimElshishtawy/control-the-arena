# core/hud.py
import pygame
from config import settings
from core import ui

class HUD:
    def __init__(self, player):
        self.player = player
        self.health = 100
        self.energy = 50
        self.max_health = 100
        self.max_energy = 50

    def draw_bar(self, surface, x, y, width, height, value, max_value, color, glow_color):
        # خلفية الشريط
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (10, 15, 25, 200), bg_rect, border_radius=6)

        # الشريط الداخلي
        fill_width = (value / max_value) * width
        fg_rect = pygame.Rect(x, y, fill_width, height)
        pygame.draw.rect(surface, color, fg_rect, border_radius=6)

        # توهج
        glow = pygame.Surface((fill_width, height), pygame.SRCALPHA)
        pygame.draw.rect(glow, glow_color, (0, 0, fill_width, height), border_radius=6)
        glow.set_alpha(90)
        surface.blit(glow, (x, y))

    def draw(self, surface):
        # health bar
        self.draw_bar(
            surface,
            20,
            20,
            200,
            18,
            self.health,
            self.max_health,
            (200, 80, 80),
            (255, 120, 120),
        )

        ui.draw_text(surface, "HEALTH", 14, settings.COLOR_TEXT, 20, 4)

        # energy bar
        self.draw_bar(
            surface,
            20,
            50,
            200,
            16,
            self.energy,
            self.max_energy,
            (80, 150, 220),
            (120, 190, 255),
        )
        ui.draw_text(surface, "ENERGY", 14, settings.COLOR_TEXT, 20, 34)
