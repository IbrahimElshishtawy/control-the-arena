# scenes/silent_orbit.py
import pygame
import math

from core.scene import Scene
from core import ui
from core.dialogue import DialogueBox
from config import settings
from entities.player import Player
from story.dialogues import (
    ORBIT_INTRO_DIALOGUE,
    ORBIT_REVELATION_ECHO,
    ORBIT_LIRA_CONFRONT_DIALOGUE,
)


class SilentOrbitScene(Scene):
    """CH-09: Quiet orbital facility – story-heavy, no enemies."""

    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.time = 0.0

        self.player = Player(settings.WIDTH // 2, settings.HEIGHT - 120)
        self.all_sprites = pygame.sprite.Group(self.player)

        # Echo zones
        self.revelation_rect = pygame.Rect(
            settings.WIDTH // 2 - 80,
            settings.HEIGHT // 2,
            160,
            40,
        )
        self.revelation_active = False
        self.revelation_done = False

        self.confront_rect = pygame.Rect(
            settings.WIDTH // 2 - 80,
            settings.HEIGHT // 2 - 80,
            160,
            40,
        )
        self.confront_active = False
        self.confront_done = False

        # Dialogues
        self.intro_dialogue = DialogueBox(ORBIT_INTRO_DIALOGUE)
        self.revelation_dialogue = None
        self.confront_dialogue = None

        # Exit to Origin Core (فصل 10)
        self.exit_rect = pygame.Rect(
            settings.WIDTH // 2 - 40,
            60,
            80,
            30,
        )
        self.exit_active = False

    def _pulse(self, speed=2.0, phase=0.0):
        return 0.5 + 0.5 * math.sin(self.time * speed + phase)

    # ---------------- Events ----------------
    def handle_events(self, events):
        if self.intro_dialogue and self.intro_dialogue.active:
            for event in events:
                self.intro_dialogue.handle_event(event)
            return

        if self.revelation_dialogue and self.revelation_dialogue.active:
            for event in events:
                self.revelation_dialogue.handle_event(event)
            return

        if self.confront_dialogue and self.confront_dialogue.active:
            for event in events:
                self.confront_dialogue.handle_event(event)
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from scenes.main_menu import MainMenu
                    self.game.change_scene(MainMenu(self.game))

                if event.key == pygame.K_e and self.revelation_active and not self.revelation_done:
                    self.revelation_done = True
                    self.revelation_dialogue = DialogueBox(ORBIT_REVELATION_ECHO)

                if event.key == pygame.K_e and self.confront_active and not self.confront_done:
                    self.confront_done = True
                    self.confront_dialogue = DialogueBox(ORBIT_LIRA_CONFRONT_DIALOGUE)

                if event.key == pygame.K_f and self.exit_active:
                    from scenes.origin_core import OriginCoreScene
                    self.game.change_scene(OriginCoreScene(self.game))

    # ---------------- Update ----------------
    def update(self, dt):
        self.time += dt
        keys = pygame.key.get_pressed()

        if (self.intro_dialogue and self.intro_dialogue.active) or \
           (self.revelation_dialogue and self.revelation_dialogue.active) or \
           (self.confront_dialogue and self.confront_dialogue.active):
            return

        self.all_sprites.update(keys)

        self.revelation_active = (not self.revelation_done) and self.player.rect.colliderect(self.revelation_rect)
        self.confront_active = (not self.confront_done) and self.player.rect.colliderect(self.confront_rect)
        self.exit_active = self.revelation_done and self.confront_done and self.player.rect.colliderect(self.exit_rect)

    # ---------------- Drawing helpers ----------------
    def _draw_background(self, surface):
        surface.fill((2, 4, 16))

        # Planet visible below
        planet_center = (settings.WIDTH // 2, settings.HEIGHT + 60)
        planet_radius = 180
        planet_surf = pygame.Surface((settings.WIDTH * 2, settings.HEIGHT * 2), pygame.SRCALPHA)
        pygame.draw.circle(planet_surf, (20, 40, 90), planet_center, planet_radius)
        surface.blit(planet_surf, (-settings.WIDTH // 2, -settings.HEIGHT // 2))

        # Window frame
        window_rect = pygame.Rect(80, 80, settings.WIDTH - 160, settings.HEIGHT // 2)
        pygame.draw.rect(surface, (8, 12, 26), window_rect)
        pygame.draw.rect(surface, (80, 110, 160), window_rect, 2)

        # Simple station floor
        floor_rect = pygame.Rect(40, window_rect.bottom + 30, settings.WIDTH - 80, settings.HEIGHT - window_rect.bottom - 70)
        pygame.draw.rect(surface, (12, 16, 30), floor_rect)
        for x in range(floor_rect.x, floor_rect.right, 40):
            pygame.draw.line(surface, (24, 30, 50), (x, floor_rect.y), (x, floor_rect.bottom), 1)

        # Exit
        gate_rect = self.exit_rect.inflate(40, 14)
        pygame.draw.rect(surface, (20, 24, 60), gate_rect, border_radius=8)
        pygame.draw.rect(surface, (190, 210, 255), gate_rect, 2, border_radius=8)
        ui.draw_centered_text(
            surface,
            "TO ORIGIN CORE",
            12,
            (210, 220, 255),
            gate_rect.centerx,
            gate_rect.y - 16,
        )

    def _draw_echo_area(self, surface, rect, label, active, done):
        if done:
            alpha = 40
        else:
            alpha = 80

        pulse = self._pulse(3.0)
        extra = int(3 * pulse)

        glow = pygame.Surface((rect.width + 30, rect.height + 30), pygame.SRCALPHA)
        pygame.draw.rect(
            glow,
            (settings.COLOR_ECHO[0], settings.COLOR_ECHO[1], settings.COLOR_ECHO[2], alpha),
            glow.get_rect(),
            border_radius=10,
        )
        pygame.draw.rect(
            glow,
            (settings.COLOR_ECHO[0], settings.COLOR_ECHO[1], settings.COLOR_ECHO[2], 160),
            pygame.Rect(8 - extra, 8 - extra, rect.width + extra * 2, rect.height + extra * 2),
            2,
            border_radius=10,
        )
        surface.blit(glow, (rect.x - 15, rect.y - 15))

        pygame.draw.rect(surface, settings.COLOR_ECHO, rect, 2, border_radius=8)
        ui.draw_centered_text(surface, label, 12, settings.COLOR_ECHO, rect.centerx, rect.centery - 18)

        if active and not done:
            ui.draw_centered_text(
                surface,
                "Press [E] to sync this Echo.",
                12,
                (200, 230, 255),
                rect.centerx,
                rect.centery + 18,
            )

    def _draw_hud(self, surface):
        ui.draw_text(surface, "Echoes of the Last Core // CH-09: SILENT ORBIT", 14, settings.COLOR_TEXT, 20, 10)
        ui.draw_text(surface, "Move: W/A/S/D or Arrows   ·   Menu: ESC", 12, settings.COLOR_TEXT, 20, 32)

        pulse = self._pulse(2.0)
        color = (160 + int(40 * pulse), 220, 255)
        ui.draw_text(
            surface,
            "Objective: Uncover what really happened in the earlier reboot cycles.",
            14,
            color,
            20,
            70,
        )

        if self.exit_active:
            ui.draw_text(
                surface,
                "Press [F] to travel to the Origin Core.",
                13,
                (210, 230, 255),
                20,
                92,
            )

    # ---------------- Draw ----------------
    def draw(self, surface):
        self._draw_background(surface)

        self._draw_echo_area(
            surface,
            self.revelation_rect,
            "REVELATION LOG",
            self.revelation_active,
            self.revelation_done,
        )
        self._draw_echo_area(
            surface,
            self.confront_rect,
            "LIRA CONFRONT",
            self.confront_active,
            self.confront_done,
        )

        self.all_sprites.draw(surface)
        self._draw_hud(surface)

        if self.intro_dialogue and self.intro_dialogue.active:
            self.intro_dialogue.draw(surface)
        elif self.revelation_dialogue and self.revelation_dialogue.active:
            self.revelation_dialogue.draw(surface)
        elif self.confront_dialogue and self.confront_dialogue.active:
            self.confront_dialogue.draw(surface)
