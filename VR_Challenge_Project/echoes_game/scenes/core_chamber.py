# scenes/core_chamber.py
import pygame
import math

from core.scene import Scene
from core import ui
from core.dialogue import DialogueBox
from config import settings
from entities.player import Player
from story.dialogues import (
    CORE_INTRO_DIALOGUE,
    CORE_FINAL_CHOICE_INTRO,
    CORE_FINAL_CHOICE_ENDING_RESET,
    CORE_FINAL_CHOICE_ENDING_PRESERVE,
)


class CoreChamberScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.time = 0.0

        # Player
        self.player = Player(settings.WIDTH // 2, settings.HEIGHT - 120)
        self.all_sprites = pygame.sprite.Group(self.player)

        # Core center
        self.core_rect = pygame.Rect(
            settings.WIDTH // 2 - 40,
            settings.HEIGHT // 2 - 60,
            80,
            120,
        )

        # Choice terminals
        self.reset_rect = pygame.Rect(
            settings.WIDTH // 2 - 200,
            settings.HEIGHT // 2 + 60,
            140,
            50,
        )
        self.preserve_rect = pygame.Rect(
            settings.WIDTH // 2 + 60,
            settings.HEIGHT // 2 + 60,
            140,
            50,
        )

        self.reset_active = False
        self.preserve_active = False

        # Dialogue phases
        self.intro_dialogue = DialogueBox(CORE_INTRO_DIALOGUE)
        self.choice_intro_dialogue = None
        self.ending_dialogue = None

        # Which ending selected
        self.selected_ending = None

    # -------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------
    def _pulse(self, speed=2.0, phase=0.0):
        return 0.5 + 0.5 * math.sin(self.time * speed + phase)

    # -------------------------------------------------------------
    # Events
    # -------------------------------------------------------------
    def handle_events(self, events):
        # Handle dialogue sequences
        if self.intro_dialogue and self.intro_dialogue.active:
            for event in events:
                self.intro_dialogue.handle_event(event)
            return

        if self.choice_intro_dialogue and self.choice_intro_dialogue.active:
            for event in events:
                self.choice_intro_dialogue.handle_event(event)
            return

        if self.ending_dialogue and self.ending_dialogue.active:
            for event in events:
                self.ending_dialogue.handle_event(event)
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from scenes.main_menu import MainMenu
                    self.game.change_scene(MainMenu(self.game))

                # أول ضغطة 1 / 2 تفتح حوار المواجهة مع Seraph
                if self.choice_intro_dialogue is None and (event.key in (pygame.K_1, pygame.K_2)):
                    self.choice_intro_dialogue = DialogueBox(CORE_FINAL_CHOICE_INTRO)
                    self.selected_ending = "reset" if event.key == pygame.K_1 else "preserve"
                    return

                # بعد حوار المواجهة، 1/2 تؤكد النهاية وتفتح حوار النهاية
                if self.choice_intro_dialogue is not None and not (self.ending_dialogue and self.ending_dialogue.active):
                    if event.key == pygame.K_1:
                        self.selected_ending = "reset"
                        self.ending_dialogue = DialogueBox(CORE_FINAL_CHOICE_ENDING_RESET)
                    elif event.key == pygame.K_2:
                        self.selected_ending = "preserve"
                        self.ending_dialogue = DialogueBox(CORE_FINAL_CHOICE_ENDING_PRESERVE)

    # -------------------------------------------------------------
    # Update
    # -------------------------------------------------------------
    def update(self, dt):
        self.time += dt

        # لو أي حوار شغّال، ما فيش حركة
        if (self.intro_dialogue and self.intro_dialogue.active) or \
           (self.choice_intro_dialogue and self.choice_intro_dialogue.active) or \
           (self.ending_dialogue and self.ending_dialogue.active):
            return

        # لو في حوار نهاية واتقفَل (active = False) → مباشرة ننتقل للمرحلة اللي بعدها
        if self.ending_dialogue and not self.ending_dialogue.active:
            from scenes.ruined_archive import RuinedArchiveScene
            self.game.change_scene(RuinedArchiveScene(self.game))
            return

        keys = pygame.key.get_pressed()
        self.all_sprites.update(keys)

        # Detect if player stands near terminals (just for hints)
        self.reset_active = self.player.rect.colliderect(self.reset_rect)
        self.preserve_active = self.player.rect.colliderect(self.preserve_rect)

    # -------------------------------------------------------------
    # Drawing helpers
    # -------------------------------------------------------------
    def _draw_core_background(self, surface):
        surface.fill((5, 4, 14))

        # Concentric circles of energy
        center = (settings.WIDTH // 2, settings.HEIGHT // 2)
        for i in range(5):
            radius = 60 + i * 35
            alpha = 30 + i * 20
            circle_surf = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(circle_surf, (80, 120, 255, alpha), center, radius, 2)
            surface.blit(circle_surf, (0, 0))

        # Core column
        pygame.draw.rect(surface, (30, 40, 80), self.core_rect, border_radius=12)
        inner = self.core_rect.inflate(-10, -10)
        pulse = self._pulse(speed=3.0)
        pygame.draw.rect(surface, (140, 190, 255), inner, 0, border_radius=10)
        glow_alpha = int(80 + 70 * pulse)
        glow_surf = pygame.Surface((inner.width, inner.height), pygame.SRCALPHA)
        glow_surf.fill((180, 220, 255, glow_alpha))
        surface.blit(glow_surf, inner.topleft, special_flags=pygame.BLEND_RGBA_ADD)

        ui.draw_centered_text(
            surface,
            "BACKUP CORE INTERFACE",
            14,
            (210, 220, 255),
            self.core_rect.centerx,
            self.core_rect.y - 24,
        )

    def _draw_terminals(self, surface):
        # Reset terminal (left)
        reset_color = (220, 150, 150)
        preserve_color = (150, 220, 180)

        for rect, label, color, active, key_label in [
            (self.reset_rect, "RESET TIMELINE", reset_color, self.reset_active, "[1]"),
            (self.preserve_rect, "PRESERVE THIS BRANCH", preserve_color, self.preserve_active, "[2]"),
        ]:
            pulse = self._pulse(speed=2.5)
            base = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
            alpha = 40 + int(40 * pulse)
            pygame.draw.rect(base, (color[0], color[1], color[2], alpha), base.get_rect(), border_radius=10)
            surface.blit(base, (rect.x - 10, rect.y - 10))

            pygame.draw.rect(surface, (25, 30, 45), rect, border_radius=8)
            pygame.draw.rect(surface, color, rect, 2, border_radius=8)

            ui.draw_centered_text(
                surface,
                label,
                12,
                color,
                rect.centerx,
                rect.centery - 4,
            )
            ui.draw_centered_text(
                surface,
                key_label,
                10,
                (220, 230, 240),
                rect.centerx,
                rect.centery + 14,
            )

    def _draw_hud(self, surface):
        ui.draw_text(surface, "Echoes of the Last Core // CH-06: CORE CHAMBER", 14, settings.COLOR_TEXT, 20, 10)
        ui.draw_text(surface, "Menu: ESC", 12, (180, 190, 210), 20, 32)

        line_pulse = self._pulse(speed=2.0)
        color = (
            160 + int(40 * line_pulse),
            220,
            255,
        )

        if not self.selected_ending:
            text = "Objective: Approach the Core and decide the fate of all branches."
        else:
            if self.selected_ending == "reset":
                text = "You chose to RESET the timeline. The Core is obeying."
            else:
                text = "You chose to PRESERVE this branch. The Core is stabilizing around it."

        ui.draw_text(
            surface,
            text,
            14,
            color,
            20,
            54,
        )

    # -------------------------------------------------------------
    # Draw
    # -------------------------------------------------------------
    def draw(self, surface):
        self._draw_core_background(surface)
        self._draw_terminals(surface)

        self.all_sprites.draw(surface)
        self._draw_hud(surface)

        # Dialogues overlays
        if self.intro_dialogue and self.intro_dialogue.active:
            self.intro_dialogue.draw(surface)
        elif self.choice_intro_dialogue and self.choice_intro_dialogue.active:
            self.choice_intro_dialogue.draw(surface)
        elif self.ending_dialogue and self.ending_dialogue.active:
            self.ending_dialogue.draw(surface)
