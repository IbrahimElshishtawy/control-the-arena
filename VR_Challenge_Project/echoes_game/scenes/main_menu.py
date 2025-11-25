# scenes/main_menu.py
import pygame
from core.scene import Scene
from core import ui
from config import settings

class MainMenu(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.options = ["ابدأ اللعبة", "خروج"]
        self.selected = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.selected == 0:
                        # لتجنب الـ circular import
                        from scenes.lab_scene import LabScene
                        self.game.change_scene(LabScene(self.game))
                    else:
                        self.game.running = False

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(settings.COLOR_BG)

        ui.draw_centered_text(
            surface,
            "Echoes of the Last Core",
            36,
            settings.COLOR_HIGHLIGHT,
            settings.WIDTH // 2,
            settings.HEIGHT // 2 - 120,
        )

        ui.draw_centered_text(
            surface,
            "Prototype - Chapter 1: The Awakening",
            18,
            settings.COLOR_TEXT,
            settings.WIDTH // 2,
            settings.HEIGHT // 2 - 80,
        )

        for i, opt in enumerate(self.options):
            color = settings.COLOR_HIGHLIGHT if i == self.selected else settings.COLOR_TEXT
            ui.draw_centered_text(
                surface,
                opt,
                24,
                color,
                settings.WIDTH // 2,
                settings.HEIGHT // 2 + i * 40,
            )
