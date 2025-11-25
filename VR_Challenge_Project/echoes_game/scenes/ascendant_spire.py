# scenes/ascendant_spire.py
import pygame
import math

from core.scene import Scene
from core import ui
from core.dialogue import DialogueBox
from config import settings
from entities.player import Player
from entities.enemy import Enemy
from story.dialogues import ASCENDANT_INTRO_DIALOGUE, ASCENDANT_SERAPH_ECHO


class AscendantSpireScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.time = 0.0

        # Player starts at bottom of the tower interior
        self.player = Player(settings.WIDTH // 2, settings.HEIGHT - 100)
        self.all_sprites = pygame.sprite.Group(self.player)

        # Enemies (Ascendant patrols)
        self.enemies = pygame.sprite.Group()
        self._spawn_enemies()

        # Memory Echo with Seraph
        self.echo_rect = pygame.Rect(
            settings.WIDTH // 2 - 40,
            settings.HEIGHT // 2,
            80,
            60,
        )
        self.echo_active = False
        self.echo_done = False
        self.echo_dialogue = None

        # Gate to Core Chamber (top center)
        self.core_gate_rect = pygame.Rect(
            settings.WIDTH // 2 - 40,
            40,
            80,
            50,
        )
        self.core_gate_active = False

        # Intro dialogue
        self.dialogue = DialogueBox(ASCENDANT_INTRO_DIALOGUE)

        # Death state
        self.player_dead = False

    # -------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------
    def _pulse(self, speed=2.0, phase=0.0):
        return 0.5 + 0.5 * math.sin(self.time * speed + phase)

    def _spawn_enemies(self):
        """Enemies patrolling different platforms."""
        y1 = settings.HEIGHT // 2 + 40
        y2 = settings.HEIGHT // 2 - 10

        e1 = Enemy(settings.WIDTH // 2 - 160, y1, patrol_width=220, speed=2, max_health=70)
        e2 = Enemy(settings.WIDTH // 2 + 140, y2, patrol_width=200, speed=3, max_health=70)

        self.enemies.add(e1, e2)

    # -------------------------------------------------------------
    # Events
    # -------------------------------------------------------------
    def handle_events(self, events):
        if self.player_dead:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        from scenes.ascendant_spire import AscendantSpireScene
                        self.game.change_scene(AscendantSpireScene(self.game))
                    elif event.key == pygame.K_ESCAPE:
                        from scenes.main_menu import MainMenu
                        self.game.change_scene(MainMenu(self.game))
            return

        if self.dialogue and self.dialogue.active:
            for event in events:
                self.dialogue.handle_event(event)
            return

        if self.echo_dialogue and self.echo_dialogue.active:
            for event in events:
                self.echo_dialogue.handle_event(event)
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from scenes.main_menu import MainMenu
                    self.game.change_scene(MainMenu(self.game))

                # Travel to Core Chamber when gate is active
                if event.key == pygame.K_f and self.core_gate_active:
                    from scenes.core_chamber import CoreChamberScene
                    self.game.change_scene(CoreChamberScene(self.game))

    # -------------------------------------------------------------
    # Update
    # -------------------------------------------------------------
    def update(self, dt):
        self.time += dt
        keys = pygame.key.get_pressed()

        if self.player_dead:
            return

        if self.dialogue and self.dialogue.active:
            return
        if self.echo_dialogue and self.echo_dialogue.active:
            return

        self.all_sprites.update(keys)
        self.enemies.update()

        # Enemy damage (no damage during Dash)
        if self.player.is_alive():
            hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
            if hits and not self.player.is_dashing:
                self.player.take_damage(15)

        # Player attack vs enemies
        if self.player.is_attacking() and self.player.can_hit_this_swing():
            attack_rect = self.player.get_attack_rect()
            if attack_rect:
                for enemy in list(self.enemies):
                    if enemy.rect.colliderect(attack_rect):
                        enemy.take_damage(self.player.attack_damage)
                        self.player.register_attack_hit()
                        break

        if not self.player.is_alive():
            self.player_dead = True

        # Echo zone
        if (not self.echo_done) and self.player.rect.colliderect(self.echo_rect):
            self.echo_active = True
        else:
            self.echo_active = False

        if self.echo_active and keys[pygame.K_e] and not self.echo_dialogue:
            self.echo_done = True
            self.echo_dialogue = DialogueBox(ASCENDANT_SERAPH_ECHO)

        # Gate to Core Chamber – لا يُفعّل إلا بعد الـ Echo
        if self.echo_done and self.player.rect.colliderect(self.core_gate_rect):
            self.core_gate_active = True
        else:
            self.core_gate_active = False

    # -------------------------------------------------------------
    # Drawing helpers
    # -------------------------------------------------------------
    def _draw_tower_background(self, surface):
        surface.fill((8, 8, 18))

        # Vertical shafts / cables
        for x in range(100, settings.WIDTH, 80):
            pygame.draw.line(surface, (50, 70, 130), (x, 0), (x, settings.HEIGHT), 1)

        # Platforms
        plat_color = (25, 30, 55)
        border_color = (120, 150, 210)

        mid_y = settings.HEIGHT // 2 + 40
        pygame.draw.rect(surface, plat_color, (80, mid_y, settings.WIDTH - 160, 10))
        pygame.draw.rect(surface, border_color, (80, mid_y, settings.WIDTH - 160, 10), 1)

        upper_y = settings.HEIGHT // 2 - 10
        pygame.draw.rect(surface, plat_color, (100, upper_y, settings.WIDTH - 200, 10))
        pygame.draw.rect(surface, border_color, (100, upper_y, settings.WIDTH - 200, 10), 1)

        # Gate to Core
        gate_rect = self.core_gate_rect.inflate(40, 20)
        pulse = self._pulse(speed=3.0)
        pygame.draw.rect(surface, (25, 20, 60), gate_rect, border_radius=8)
        pygame.draw.rect(surface, (180, 210, 255), gate_rect, 2, border_radius=8)

        ui.draw_centered_text(
            surface,
            "CORE INTERFACE",
            12,
            (210, 220, 255),
            gate_rect.centerx,
            gate_rect.y - 16,
        )

    def _draw_echo_zone(self, surface):
        if self.echo_done:
            base_alpha = 40
        else:
            base_alpha = 80

        pulse = self._pulse(speed=3.0)
        extra = int(4 * pulse)

        glow_surface = pygame.Surface((self.echo_rect.width + 40, self.echo_rect.height + 40), pygame.SRCALPHA)

        pygame.draw.rect(
            glow_surface,
            (settings.COLOR_ECHO[0], settings.COLOR_ECHO[1], settings.COLOR_ECHO[2], base_alpha),
            glow_surface.get_rect(),
            border_radius=12,
        )

        pygame.draw.rect(
            glow_surface,
            (settings.COLOR_ECHO[0], settings.COLOR_ECHO[1], settings.COLOR_ECHO[2], 160),
            pygame.Rect(
                10 - extra,
                10 - extra,
                self.echo_rect.width + extra * 2,
                self.echo_rect.height + extra * 2,
            ),
            2,
            border_radius=12,
        )

        surface.blit(glow_surface, (self.echo_rect.x - 20, self.echo_rect.y - 20))

        pygame.draw.rect(surface, settings.COLOR_ECHO, self.echo_rect, 2, border_radius=8)

        ui.draw_centered_text(
            surface,
            "SERAPH ECHO",
            12,
            settings.COLOR_ECHO,
            self.echo_rect.centerx,
            self.echo_rect.centery - 18,
        )

        if self.echo_active and not self.echo_dialogue:
            ui.draw_centered_text(
                surface,
                "Press [E] to sync this Echo.",
                12,
                (200, 230, 255),
                self.echo_rect.centerx,
                self.echo_rect.centery + 22,
            )

    def _draw_attack_effect(self, surface):
        """Visual glow showing where the melee swing is hitting."""
        if not hasattr(self.player, "is_attacking"):
            return
        if not self.player.is_attacking():
            return

        attack_rect = self.player.get_attack_rect()
        if not attack_rect:
            return

        glow_w = attack_rect.width + 24
        glow_h = attack_rect.height + 24
        glow_surf = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)

        r, g, b = settings.COLOR_HIGHLIGHT
        base_alpha = 90

        pygame.draw.rect(
            glow_surf,
            (r, g, b, base_alpha),
            glow_surf.get_rect(),
            border_radius=10,
        )
        pygame.draw.rect(
            glow_surf,
            (r, g, b, 180),
            glow_surf.get_rect().inflate(-6, -6),
            2,
            border_radius=10,
        )

        surface.blit(glow_surf, (attack_rect.x - 12, attack_rect.y - 12))

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

    def _draw_death_overlay(self, surface):
        if not self.player_dead:
            return

        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))

        ui.draw_centered_text(
            surface,
            "ASCENT FAILED",
            32,
            (255, 150, 150),
            settings.WIDTH // 2,
            settings.HEIGHT // 2 - 20,
        )
        ui.draw_centered_text(
            surface,
            "You were taken down by Ascendant patrols.",
            16,
            (220, 200, 220),
            settings.WIDTH // 2,
            settings.HEIGHT // 2 + 10,
        )
        ui.draw_centered_text(
            surface,
            "Press [R] to retry the Spire · Press [ESC] for Main Menu",
            14,
            (200, 200, 220),
            settings.WIDTH // 2,
            settings.HEIGHT // 2 + 40,
        )

    def _draw_hud(self, surface):
        ui.draw_text(surface, "Echoes of the Last Core // CH-05: ASCENDANT SPIRE", 14, settings.COLOR_TEXT, 20, 10)
        ui.draw_text(surface, "Move: W / A / S / D or Arrow keys", 12, settings.COLOR_TEXT, 20, 32)
        ui.draw_text(surface, "Menu: ESC   ·   Ascendant patrols will damage you", 12, (180, 190, 210), 20, 48)

        objective_pulse = self._pulse(speed=2.0)
        color = (
            160 + int(40 * objective_pulse),
            220,
            255,
        )
        ui.draw_text(
            surface,
            "Objective: Survive the ascent, sync Seraph's Echo, then reach the Core interface.",
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

        if self.core_gate_active:
            ui.draw_text(
                surface,
                "Press [F] to enter the Core Chamber.",
                13,
                (210, 230, 255),
                20,
                114,
            )

        self._draw_health_bar(
            surface,
            20,
            settings.HEIGHT - 32,
            220,
            14,
            self.player.health,
            self.player.max_health,
        )

    # -------------------------------------------------------------
    # Draw
    # -------------------------------------------------------------
    def draw(self, surface):
        self._draw_tower_background(surface)
        self._draw_echo_zone(surface)

        self.all_sprites.draw(surface)
        self.enemies.draw(surface)

        # Attack glow effect
        self._draw_attack_effect(surface)

        self._draw_hud(surface)
        self._draw_death_overlay(surface)

        if self.dialogue and self.dialogue.active:
            self.dialogue.draw(surface)
        elif self.echo_dialogue and self.echo_dialogue.active:
            self.echo_dialogue.draw(surface)
