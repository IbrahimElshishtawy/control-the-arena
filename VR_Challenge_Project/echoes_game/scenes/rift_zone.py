# scenes/rift_zone.py
import pygame
import math

from core.scene import Scene
from core import ui
from core.dialogue import DialogueBox
from config import settings
from entities.player import Player
from entities.enemy import Enemy
from story.dialogues import RIFT_INTRO_DIALOGUE, RIFT_ALT_PATH_ECHO, RIFT_REVEAL_ECHO


class RiftZoneScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.time = 0.0

        # Player starts near bottom-center
        self.player = Player(settings.WIDTH // 2, settings.HEIGHT - 100)
        self.all_sprites = pygame.sprite.Group(self.player)

        # Enemies (corrupted echoes)
        self.enemies = pygame.sprite.Group()
        self._spawn_enemies()

        # Two Echo zones
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

        # Gateway to Keepers Facility – appears effectively after both echoes collected
        self.gate_rect = pygame.Rect(
            settings.WIDTH // 2 - 40,
            40,
            80,
            60,
        )
        self.gate_active = False

        # Intro dialogue
        self.dialogue = DialogueBox(RIFT_INTRO_DIALOGUE)

        # Echo dialogues
        self.alt_echo_dialogue = None
        self.reveal_echo_dialogue = None

        # Death state
        self.player_dead = False

    # -------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------
    def _pulse(self, speed=2.0, phase=0.0):
        return 0.5 + 0.5 * math.sin(self.time * speed + phase)

    def _spawn_enemies(self):
        """Spawn a couple of 'corrupted echoes' as enemies."""
        y1 = settings.HEIGHT // 2 + 40
        y2 = settings.HEIGHT // 2 - 20

        e1 = Enemy(settings.WIDTH // 2 - 160, y1, patrol_width=220, speed=2, max_health=60)
        e2 = Enemy(settings.WIDTH // 2 + 140, y2, patrol_width=200, speed=3, max_health=60)

        self.enemies.add(e1, e2)

    def _both_echoes_synced(self) -> bool:
        return self.alt_echo_collected and self.reveal_echo_collected

    # -------------------------------------------------------------
    # Events
    # -------------------------------------------------------------
    def handle_events(self, events):
        # If player is dead: handle only restart / menu
        if self.player_dead:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        from scenes.rift_zone import RiftZoneScene
                        self.game.change_scene(RiftZoneScene(self.game))
                    elif event.key == pygame.K_ESCAPE:
                        from scenes.main_menu import MainMenu
                        self.game.change_scene(MainMenu(self.game))
            return

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

                # Travel to Keepers Facility when gate is active
                if event.key == pygame.K_f and self.gate_active and self._both_echoes_synced():
                    from scenes.keepers_facility import KeepersFacilityScene
                    self.game.change_scene(KeepersFacilityScene(self.game))

    # -------------------------------------------------------------
    # Update
    # -------------------------------------------------------------
    def update(self, dt):
        self.time += dt
        keys = pygame.key.get_pressed()

        if self.player_dead:
            return

        # Stop when dialogues are active
        if self.dialogue and self.dialogue.active:
            return
        if (self.alt_echo_dialogue and self.alt_echo_dialogue.active) or \
           (self.reveal_echo_dialogue and self.reveal_echo_dialogue.active):
            return

        # Update movement
        self.all_sprites.update(keys)
        self.enemies.update()

        # Enemy collision / damage (لا ضرر أثناء الـ Dash)
        if self.player.is_alive():
            hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
            if hits and not self.player.is_dashing:
                self.player.take_damage(10)

        # Player attack vs enemies
        if self.player.is_attacking() and self.player.can_hit_this_swing():
            attack_rect = self.player.get_attack_rect()
            if attack_rect:
                for enemy in list(self.enemies):
                    if enemy.rect.colliderect(attack_rect):
                        enemy.take_damage(self.player.attack_damage)
                        self.player.register_attack_hit()
                        break

        # Death check
        if not self.player.is_alive():
            self.player_dead = True

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

        # Gate activation only makes sense once both echoes are synced
        if self._both_echoes_synced() and self.player.rect.colliderect(self.gate_rect):
            self.gate_active = True
        else:
            self.gate_active = False

    # -------------------------------------------------------------
    # Drawing helpers
    # -------------------------------------------------------------
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

        # Vertical fractures
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

    def _draw_gate(self, surface):
        """Visual gate to Keepers Facility (only makes sense once both echoes are synced)."""
        if not self._both_echoes_synced():
            return

        pulse = self._pulse(speed=3.5)
        extra = int(4 * pulse)

        # Gate body
        gate_surface = pygame.Surface((self.gate_rect.width + 30, self.gate_rect.height + 30), pygame.SRCALPHA)

        pygame.draw.rect(
            gate_surface,
            (40, 0, 80, 120),
            (0, 0, gate_surface.get_width(), gate_surface.get_height()),
            border_radius=12,
        )

        pygame.draw.rect(
            gate_surface,
            (120 + int(80 * pulse), 200, 255, 220),
            pygame.Rect(
                10 - extra,
                10 - extra,
                self.gate_rect.width + extra * 2,
                self.gate_rect.height + extra * 2,
            ),
            2,
            border_radius=12,
        )

        surface.blit(gate_surface, (self.gate_rect.x - 15, self.gate_rect.y - 15))

        ui.draw_centered_text(
            surface,
            "KEEPERS FACILITY LINK",
            12,
            (200, 230, 255),
            self.gate_rect.centerx,
            self.gate_rect.y - 14,
        )

        if self.gate_active:
            ui.draw_centered_text(
                surface,
                "Press [F] to anchor this branch",
                12,
                (200, 240, 255),
                self.gate_rect.centerx,
                self.gate_rect.bottom + 16,
            )

    def _draw_health_bar(self, surface, x, y, width, height, value, max_value):
        ratio = max(0, min(1, value / max_value if max_value > 0 else 0))
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (15, 20, 30), bg_rect, border_radius=6)

        if ratio > 0:
            fg_rect = pygame.Rect(x, y, int(width * ratio), height)
            pygame.draw.rect(surface, (200, 80, 80), fg_rect, border_radius=6)
            glow = pygame.Surface((fg_rect.width, height), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 120, 120, 90), (0, 0, fg_rect.width, height), border_radius=6)
            surface.blit(glow, (x, y))

        pygame.draw.rect(surface, (120, 40, 40), bg_rect, 2, border_radius=6)
        ui.draw_text(surface, "HP", 12, settings.COLOR_TEXT, x - 28, y - 2)

    def _draw_hud(self, surface):
        ui.draw_text(surface, "Echoes of the Last Core // CH-03: RIFT ZONE", 14, settings.COLOR_TEXT, 20, 10)
        ui.draw_text(surface, "Move: W / A / S / D or Arrow keys", 12, settings.COLOR_TEXT, 20, 32)
        ui.draw_text(surface, "Menu: ESC   ·   Corrupted echoes will damage you", 12, (180, 190, 210), 20, 48)

        objective_pulse = self._pulse(speed=2.2)
        color = (
            160 + int(40 * objective_pulse),
            220,
            255,
        )

        if not self._both_echoes_synced():
            text = "Objective: Sync both Echo nodes to stabilize your identity."
        else:
            text = "Objective: Reach the gate and anchor this branch with the Keepers."

        ui.draw_text(
            surface,
            text,
            14,
            color,
            20,
            70,
        )

        ui.draw_text(
            surface,
            "Combat: J = melee attack   ·   K = dash",
            12,
            (190, 200, 230),
            20,
            92,
        )

        # Health bar bottom-left
        self._draw_health_bar(
            surface,
            20,
            settings.HEIGHT - 32,
            220,
            14,
            self.player.health,
            self.player.max_health,
        )

    def _draw_death_overlay(self, surface):
        if not self.player_dead:
            return

        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))

        ui.draw_centered_text(
            surface,
            "CONNECTION LOST",
            32,
            (255, 150, 190),
            settings.WIDTH // 2,
            settings.HEIGHT // 2 - 20,
        )
        ui.draw_centered_text(
            surface,
            "Your identity stream collapsed inside the Rift.",
            16,
            (220, 200, 230),
            settings.WIDTH // 2,
            settings.HEIGHT // 2 + 10,
        )
        ui.draw_centered_text(
            surface,
            "Press [R] to re-sync from the Rift Zone · Press [ESC] for Main Menu",
            14,
            (200, 200, 220),
            settings.WIDTH // 2,
            settings.HEIGHT // 2 + 40,
        )

    # -------------------------------------------------------------
    # Draw
    # -------------------------------------------------------------
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

        # Gate to Keepers Facility (after echoes synced)
        self._draw_gate(surface)

        # Player + enemies
        self.all_sprites.draw(surface)
        self.enemies.draw(surface)

        # HUD + death overlay
        self._draw_hud(surface)
        self._draw_death_overlay(surface)

        # Dialogues
        if self.dialogue and self.dialogue.active:
            self.dialogue.draw(surface)
        elif self.alt_echo_dialogue and self.alt_echo_dialogue.active:
            self.alt_echo_dialogue.draw(surface)
        elif self.reveal_echo_dialogue and self.reveal_echo_dialogue.active:
            self.reveal_echo_dialogue.draw(surface)
