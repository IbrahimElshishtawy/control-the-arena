# scenes/keepers_facility.py
import pygame
import math

from core.scene import Scene
from core import ui
from core.dialogue import DialogueBox
from config import settings
from entities.player import Player
from story.dialogues import (
    KEEPERS_INTRO_DIALOGUE,
    KEEPERS_MEETING_DIALOGUE,
    KEEPERS_SECRET_ECHO,
)


class KeepersFacilityScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.time = 0.0

        # Player starts near bottom-center of the facility room
        self.player = Player(settings.WIDTH // 2, settings.HEIGHT - 120)
        self.all_sprites = pygame.sprite.Group(self.player)

        # Meeting area (Commander Hale)
        self.meeting_rect = pygame.Rect(
            settings.WIDTH // 2 - 60,
            settings.HEIGHT // 2 - 60,
            120,
            80,
        )
        self.meeting_active = False
        self.meeting_done = False

        # Secret echo terminal
        self.secret_echo_rect = pygame.Rect(
            120,
            settings.HEIGHT // 2 - 30,
            80,
            60,
        )
        self.secret_echo_active = False
        self.secret_echo_done = False

        # Dialogues
        self.intro_dialogue = DialogueBox(KEEPERS_INTRO_DIALOGUE)
        self.meeting_dialogue = None
        self.secret_echo_dialogue = None

    # -------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------
    def _pulse(self, speed=2.0, phase=0.0):
        return 0.5 + 0.5 * math.sin(self.time * speed + phase)

    # -------------------------------------------------------------
    # Events
    # -------------------------------------------------------------
    def handle_events(self, events):
        # Dialogues priority
        if self.intro_dialogue and self.intro_dialogue.active:
            for event in events:
                self.intro_dialogue.handle_event(event)
            return

        if self.meeting_dialogue and self.meeting_dialogue.active:
            for event in events:
                self.meeting_dialogue.handle_event(event)
            return

        if self.secret_echo_dialogue and self.secret_echo_dialogue.active:
            for event in events:
                self.secret_echo_dialogue.handle_event(event)
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from scenes.main_menu import MainMenu
                    self.game.change_scene(MainMenu(self.game))

                # Trigger meeting with Hale
                if event.key == pygame.K_e and self.meeting_active and not self.meeting_done:
                    self.meeting_dialogue = DialogueBox(KEEPERS_MEETING_DIALOGUE)
                    self.meeting_done = True

                # Trigger secret Memory Echo
                if event.key == pygame.K_e and self.secret_echo_active and not self.secret_echo_done:
                    self.secret_echo_dialogue = DialogueBox(KEEPERS_SECRET_ECHO)
                    self.secret_echo_done = True

    # -------------------------------------------------------------
    # Update
    # -------------------------------------------------------------
    def update(self, dt):
        self.time += dt
        keys = pygame.key.get_pressed()

        # Stop movement while any dialogue is active
        if (self.intro_dialogue and self.intro_dialogue.active) or \
           (self.meeting_dialogue and self.meeting_dialogue.active) or \
           (self.secret_echo_dialogue and self.secret_echo_dialogue.active):
            return

        self.all_sprites.update(keys)

        # Check meeting area
        if self.player.rect.colliderect(self.meeting_rect):
            self.meeting_active = True
        else:
            self.meeting_active = False

        # Check secret echo terminal
        if self.player.rect.colliderect(self.secret_echo_rect):
            self.secret_echo_active = True
        else:
            self.secret_echo_active = False

    # -------------------------------------------------------------
    # Drawing helpers
    # -------------------------------------------------------------
    def _draw_facility_background(self, surface):
        # Base dark
        surface.fill((5, 8, 18))

        # Main room
        room_rect = pygame.Rect(80, 60, settings.WIDTH - 160, settings.HEIGHT - 160)
        pygame.draw.rect(surface, (18, 28, 45), room_rect)
        pygame.draw.rect(surface, (80, 110, 150), room_rect, 2)

        # Floor grid
        grid_color = (35, 50, 80)
        spacing = 50
        for x in range(room_rect.x + 20, room_rect.right - 20, spacing):
            pygame.draw.line(surface, grid_color, (x, room_rect.y + 20), (x, room_rect.bottom - 20), 1)
        for y in range(room_rect.y + 20, room_rect.bottom - 20, spacing):
            pygame.draw.line(surface, grid_color, (room_rect.x + 20, y), (room_rect.right - 20, y), 1)

        # Meeting area platform
        platform_rect = self.meeting_rect.inflate(80, 40)
        pygame.draw.rect(surface, (25, 35, 60), platform_rect, border_radius=12)
        pygame.draw.rect(surface, (120, 150, 200), platform_rect, 2, border_radius=12)

        ui.draw_centered_text(
            surface,
            "KEEPERS COMMAND NODE",
            12,
            (190, 210, 240),
            platform_rect.centerx,
            platform_rect.y - 16,
        )

        # Secret console
        console_rect = self.secret_echo_rect.inflate(40, 20)
        pygame.draw.rect(surface, (25, 30, 55), console_rect, border_radius=8)
        pygame.draw.rect(surface, (160, 200, 255), console_rect, 2, border_radius=8)

        ui.draw_text(
            surface,
            "Memory Console",
            11,
            (200, 220, 255),
            console_rect.x + 4,
            console_rect.y - 14,
        )

    def _draw_interaction_highlights(self, surface):
        pulse = self._pulse(speed=3.0)

        # Meeting halo
        if not self.meeting_done:
            halo_surface = pygame.Surface((self.meeting_rect.width + 40, self.meeting_rect.height + 40), pygame.SRCALPHA)
            pygame.draw.ellipse(
                halo_surface,
                (120, 220, 255, int(80 + 60 * pulse)),
                halo_surface.get_rect(),
            )
            surface.blit(halo_surface, (self.meeting_rect.x - 20, self.meeting_rect.y - 20))

        # Secret console halo
        if not self.secret_echo_done:
            halo_surface = pygame.Surface((self.secret_echo_rect.width + 40, self.secret_echo_rect.height + 40), pygame.SRCALPHA)
            pygame.draw.ellipse(
                halo_surface,
                (200, 140, 255, int(70 + 50 * pulse)),
                halo_surface.get_rect(),
            )
            surface.blit(halo_surface, (self.secret_echo_rect.x - 20, self.secret_echo_rect.y - 20))

    def _draw_hud(self, surface):
        ui.draw_text(surface, "Echoes of the Last Core // CH-04: KEEPERS FACILITY", 14, settings.COLOR_TEXT, 20, 10)
        ui.draw_text(surface, "Move: W / A / S / D or Arrow keys", 12, settings.COLOR_TEXT, 20, 32)
        ui.draw_text(surface, "Menu: ESC", 12, (180, 190, 210), 20, 48)

        objective_pulse = self._pulse(speed=2.1)
        color = (
            160 + int(40 * objective_pulse),
            220,
            255,
        )

        ui.draw_text(
            surface,
            "Objective: Meet Commander Hale and uncover what the Keepers really know.",
            14,
            color,
            20,
            70,
        )

        if self.meeting_active and not self.meeting_done:
            ui.draw_text(
                surface,
                "Press [E] to talk to Commander Hale.",
                13,
                (200, 230, 255),
                20,
                94,
            )

        if self.secret_echo_active and not self.secret_echo_done:
            ui.draw_text(
                surface,
                "Press [E] to access Lira's hidden Memory Console.",
                13,
                (220, 200, 255),
                20,
                114,
            )

    # -------------------------------------------------------------
    # Draw
    # -------------------------------------------------------------
    def draw(self, surface):
        self._draw_facility_background(surface)
        self._draw_interaction_highlights(surface)

        self.all_sprites.draw(surface)
        self._draw_hud(surface)

        # Dialogues
        if self.intro_dialogue and self.intro_dialogue.active:
            self.intro_dialogue.draw(surface)
        elif self.meeting_dialogue and self.meeting_dialogue.active:
            self.meeting_dialogue.draw(surface)
        elif self.secret_echo_dialogue and self.secret_echo_dialogue.active:
            self.secret_echo_dialogue.draw(surface)
