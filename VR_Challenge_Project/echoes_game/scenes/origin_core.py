# scenes/origin_core.py
import pygame
import math

from core.scene import Scene
from core import ui
from core.dialogue import DialogueBox
from config import settings
from entities.player import Player
from story.dialogues import (
    ORIGIN_INTRO_DIALOGUE,
    ORIGIN_CHOICE_SETUP,
    ORIGIN_EPILOGUE_OPEN_END,
)


class OriginCoreScene(Scene):
    """CH-10: First Origin Core, final epilogue."""

    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.time = 0.0

        self.player = Player(settings.WIDTH // 2, settings.HEIGHT - 120)
        self.all_sprites = pygame.sprite.Group(self.player)

        # Origin core
        self.core_rect = pygame.Rect(
            settings.WIDTH // 2 - 35,
            settings.HEIGHT // 2 - 50,
            70,
            100,
        )

        # Dialogues in sequence
        self.intro_dialogue = DialogueBox(ORIGIN_INTRO_DIALOGUE)
        self.setup_dialogue = None
        self.epilogue_dialogue = None

        self.sequence_done = False

    def _pulse(self, speed=2.0, phase=0.0):
        return 0.5 + 0.5 * math.sin(self.time * speed + phase)

    # ---------------- Events ----------------
    def handle_events(self, events):
        # Chain dialogues: intro → setup → epilogue
        if self.intro_dialogue and self.intro_dialogue.active:
            for event in events:
                self.intro_dialogue.handle_event(event)
            return

        if self.setup_dialogue and self.setup_dialogue.active:
            for event in events:
                self.setup_dialogue.handle_event(event)
            return

        if self.epilogue_dialogue and self.epilogue_dialogue.active:
            for event in events:
                self.epilogue_dialogue.handle_event(event)
            return

        # After all done
        if self.sequence_done:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        from scenes.main_menu import MainMenu
                        self.game.change_scene(MainMenu(self.game))
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from scenes.main_menu import MainMenu
                    self.game.change_scene(MainMenu(self.game))

                # Start setup dialogue بعد انتهاء الـ intro (أو لو intro أصلاً خلصت)
                if (not self.setup_dialogue) and (not (self.intro_dialogue and self.intro_dialogue.active)):
                    self.setup_dialogue = DialogueBox(ORIGIN_CHOICE_SETUP)

                # بعد انتهاء setup، أول ضغط أي زر يبدأ epilogue
                elif (not self.epilogue_dialogue) and (self.setup_dialogue and not self.setup_dialogue.active):
                    self.epilogue_dialogue = DialogueBox(ORIGIN_EPILOGUE_OPEN_END)

    # ---------------- Update ----------------
    def update(self, dt):
        self.time += dt
        keys = pygame.key.get_pressed()

        # لا توجد معارك هنا، لكن نسمح بالحركة الخفيفة إلا أثناء الحوار
        if (self.intro_dialogue and self.intro_dialogue.active) or \
           (self.setup_dialogue and self.setup_dialogue.active) or \
           (self.epilogue_dialogue and self.epilogue_dialogue.active):
            return

        if self.epilogue_dialogue and not self.epilogue_dialogue.active:
            self.sequence_done = True
            return

        self.all_sprites.update(keys)

    # ---------------- Drawing helpers ----------------
    def _draw_background(self, surface):
        surface.fill((3, 5, 16))

        center = (settings.WIDTH // 2, settings.HEIGHT // 2)
        for i in range(4):
            radius = 50 + i * 50
            alpha = 40 + i * 25
            circ_surf = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(circ_surf, (100, 180, 255, alpha), center, radius, 2)
            surface.blit(circ_surf, (0, 0))

        # Origin core small column
        pygame.draw.rect(surface, (20, 40, 80), self.core_rect, border_radius=10)
        inner = self.core_rect.inflate(-8, -8)
        pulse = self._pulse(2.5)
        pygame.draw.rect(surface, (140, 210, 255), inner, border_radius=8)
        glow_alpha = int(70 + 70 * pulse)
        glow = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
        glow.fill((180, 230, 255, glow_alpha))
        surface.blit(glow, inner.topleft, special_flags=pygame.BLEND_RGBA_ADD)

        ui.draw_centered_text(
            surface,
            "ORIGIN CORE",
            14,
            (210, 220, 255),
            self.core_rect.centerx,
            self.core_rect.y - 20,
        )

    def _draw_hud(self, surface):
        ui.draw_text(surface, "Echoes of the Last Core // CH-10: ORIGIN CORE", 14, settings.COLOR_TEXT, 20, 10)
        ui.draw_text(surface, "Move: W/A/S/D or Arrows   ·   Menu: ESC", 12, settings.COLOR_TEXT, 20, 32)

        pulse = self._pulse(2.0)
        color = (160 + int(40 * pulse), 220, 255)

        if not self.sequence_done:
            ui.draw_text(
                surface,
                "Objective: Listen to the Origin and define a rule the Core will remember.",
                14,
                color,
                20,
                70,
            )
        else:
            ui.draw_text(
                surface,
                "Epilogue complete. Press [ESC] to return to Main Menu.",
                14,
                (210, 220, 240),
                20,
                70,
            )

    # ---------------- Draw ----------------
    def draw(self, surface):
        self._draw_background(surface)
        self.all_sprites.draw(surface)
        self._draw_hud(surface)

        if self.intro_dialogue and self.intro_dialogue.active:
            self.intro_dialogue.draw(surface)
        elif self.setup_dialogue and self.setup_dialogue.active:
            self.setup_dialogue.draw(surface)
        elif self.epilogue_dialogue and self.epilogue_dialogue.active:
            self.epilogue_dialogue.draw(surface)
