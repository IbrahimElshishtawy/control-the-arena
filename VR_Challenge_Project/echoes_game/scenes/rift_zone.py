# scenes/rift_zone.py
import pygame
import math

from core.scene import Scene
from core import ui
from core.dialogue import DialogueBox
from config import settings
from entities.player import Player
from story.dialogues import RIFT_INTRO_DIALOGUE, RIFT_ALT_PATH_ECHO, RIFT_REVEAL_ECHO


class RiftZoneScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.time = 0.0

        # Player starts near bottom-center
        self.player = Player(settings.WIDTH // 2, settings.HEIGHT - 100)
        self.all_sprites = pygame.sprite.Group(self.player)

        # Two Echo zones: one alternate-path Echo, one big reveal Echo
        self.alt_echo_rect = pygame.Rect(
            settings.WIDTH // 2 - 120,
            settings.HEIGHT // 2 - 40,
            80,
            80,
        )
        self.reveal_echo_rect = pygame.Rect(
            settings.WIDTH // 2 + 40,
            settings.HEIGHT // 2 - 40,
            80,
            80,
        )

        self.alt_echo_active = False
        self.reveal_echo_active = False

        self.alt_echo_collected = False
        self.reveal_echo_collected = False

        # Intro dialogue
        self.dialogue = DialogueBox(RIFT_INTRO_DIALOGUE)

        # Echo dialogues
        self.alt_echo_dialogue = None
        self.reveal_echo_dialogue = None

    def _pulse(self, speed=2.0, phase=0.0):
        return 0.5 + 0.5 * math.sin(self.time * speed + phase)

    # ----------------- Events -----------------
    def handle_events(self, events):
        # While a dialogue is active, only feed it events
        if self.dialogue and self.dialogue.active:
            for event in events:
                self.dialogue.handle_event(event)
            return

        if self.alt_echo_dialogue and self.alt_echo_dialogue.active:
            for event in events:
                self.alt_echo_dialogue.handle_event(event)
            return

        if self.reveal_echo_dialogue and self.reveal_echo_dialogue.active:
            for event in events:
                self.reveal_echo_dialogue.handle_event(event)
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from scenes.main_menu import MainMenu
                    self.game.change_scene(MainMenu(self.game))

    # ----------------- Update -----------------
    def update(self, dt):
        self.time += dt
        keys = pygame.key.get_pressed()

        if self.dialogue and self.dialogue.active:
            return
        if (self.alt_echo_dialogue and self.alt_echo_dialogue.active) or \
           (self.reveal_echo_dialogue and self.reveal_echo_dialogue.active):
            return

        self.all_sprites.update(keys)

        # Check alt echo zone
        if not self.alt_echo_collected and self.player.rect.colliderect(self.alt_echo_rect):
            self.alt_echo_active = True
        else:
            self.alt_echo_active = False

        # Check reveal echo zone
        if not self.reveal_echo_collected and self.player.rect.colliderect(self.reveal_echo_rect):
            self.reveal_echo_active = True
        else:
            self.reveal_echo_active = False

        # Trigger alt path echo
        if self.alt_echo_active and keys[pygame.K_e] and not self.alt_echo_dialogue:
            self.alt_echo_collected = True
            self.alt_echo_dialogue = DialogueBox(RIFT_ALT_PATH_ECHO)

        # Trigger reveal echo
        if self.reveal_echo_active and keys[pygame.K_e] and not self.reveal_echo_dialogue:
            self.reveal_echo_collected = True
            self.reveal_echo_dialogue = DialogueBox(RIFT_REVEAL_ECHO)

    # ----------------- Drawing helpers -----------------
    def _draw_rift_background(self, surface):
        # Base color
        surface.fill((6, 6, 16))

        # Horizontal energy layers
        for i in range(6):
            y = 80 + i * 60
            intensity = 40 + i * 20
            alpha = 50 + i * 20
            layer_surface = pygame.Surface((settings.WIDTH, 40), pygame.SRCALPHA)
            pygame.draw.rect(
                layer_surface,
                (intensity, 60, 120 + intensity // 2, alpha),
                (0, 0, settings.WIDTH, 40),
            )
            surface.blit(layer_surface, (0, y))

        # Vertical “fractures”
        for x in range(0, settings.WIDTH, 60):
            height = settings.HEIGHT
            offset = int(10 * math.sin(self.time * 2 + x * 0.2))
            pygame.draw.line(
                surface,
                (80, 160, 220),
                (x + offset, 0),
                (x - offset, height),
                1,
            )

    def _draw_echo_node(self, surface, rect, color, label, active, collected):
        if collected:
            # dim if collected
            base_alpha = 40
        else:
            base_alpha = 80

        pulse = self._pulse(speed=3.0)
        extra = int(6 * pulse)

        glow_surface = pygame.Surface((rect.width + 40, rect.height + 40), pygame.SRCALPHA)

        pygame.draw.ellipse(
            glow_surface,
            (color[0], color[1], color[2], base_alpha),
            glow_surface.get_rect(),
        )

        pygame.draw.ellipse(
            glow_surface,
            (color[0], color[1], color[2], 160),
            pygame.Rect(
                10 - extra,
                10 - extra,
                rect.width + extra * 2,
                rect.height + extra * 2,
            ),
            2,
        )

        surface.blit(glow_surface, (rect.x - 20, rect.y - 20))

        pygame.draw.ellipse(surface, color, rect, 2)

        ui.draw_centered_text(
            surface,
            label,
            12,
            color,
            rect.centerx,
            rect.centery - 22,
        )

        if active and not collected:
            ui.draw_centered_text(
                surface,
                "Press [E] to sync this Echo",
                12,
                (200, 230, 255),
                rect.centerx,
                rect.centery + 30,
            )

    def _draw_hud(self, surface):
        ui.draw_text(surface, "Echoes of the Last Core // CH-03: RIFT ZONE", 14, settings.COLOR_TEXT, 20, 10)
        ui.draw_text(surface, "Move: W / A / S / D or Arrow keys", 12, settings.COLOR_TEXT, 20, 32)
        ui.draw_text(surface, "Menu: ESC", 12, (180, 190, 210), 20, 48)

        objective_pulse = self._pulse(speed=2.2)
        color = (
            160 + int(40 * objective_pulse),
            220,
            255,
        )
        ui.draw_text(
            surface,
            "Objective: Investigate the Rift Echoes. Not all of them belong to your timeline.",
            14,
            color,
            20,
            70,
        )

    # ----------------- Draw -----------------
    def draw(self, surface):
        self._draw_rift_background(surface)

        # Echo nodes
        self._draw_echo_node(
            surface,
            self.alt_echo_rect,
            settings.COLOR_ECHO,
            "ALT-PATH ECHO",
            self.alt_echo_active,
            self.alt_echo_collected,
        )

        self._draw_echo_node(
            surface,
            self.reveal_echo_rect,
            (200, 120, 255),
            "IDENTITY REVEAL",
            self.reveal_echo_active,
            self.reveal_echo_collected,
        )

        # Player
        self.all_sprites.draw(surface)

        # HUD
        self._draw_hud(surface)

        # Dialogues
        if self.dialogue and self.dialogue.active:
            self.dialogue.draw(surface)
        elif self.alt_echo_dialogue and self.alt_echo_dialogue.active:
            self.alt_echo_dialogue.draw(surface)
        elif self.reveal_echo_dialogue and self.reveal_echo_dialogue.active:
            self.reveal_echo_dialogue.draw(surface)
