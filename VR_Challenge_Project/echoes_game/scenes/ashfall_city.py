# scenes/ashfall_city.py
import pygame
import math

from core.scene import Scene
from core import ui
from core.dialogue import DialogueBox
from config import settings
from entities.player import Player
from entities.enemy import Enemy
from story.dialogues import CITY_INTRO_DIALOGUE, CITY_STREET_ECHO_1


class AshfallCityScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.time = 0.0

        # Player starts near bottom of screen
        self.player = Player(settings.WIDTH // 2, settings.HEIGHT - 100)
        self.all_sprites = pygame.sprite.Group(self.player)

        # Enemies
        self.enemies = pygame.sprite.Group()
        self._spawn_enemies()

        # Simple Memory Echo zone in the street
        self.echo_rect = pygame.Rect(
            settings.WIDTH // 2 - 50,
            settings.HEIGHT // 2 - 20,
            100,
            40,
        )
        self.echo_active = False
        self.echo_collected = False

        # Gate to Rift Zone on the far right side of the road
        self.gate_rect = pygame.Rect(
            settings.WIDTH - 120,
            settings.HEIGHT // 2 + 20,
            60,
            120,
        )
        self.gate_active = False

        # Intro dialogue for the city
        self.dialogue = DialogueBox(CITY_INTRO_DIALOGUE)

        # Echo dialogue
        self.echo_dialogue = None

        # Player death state
        self.player_dead = False

    def _spawn_enemies(self):
        """Create a couple of patrolling enemies on the road."""
        road_y = settings.HEIGHT // 2 + 80

        e1 = Enemy(settings.WIDTH // 2 - 140, road_y, patrol_width=200, speed=2)
        e2 = Enemy(settings.WIDTH // 2 + 80, road_y, patrol_width=180, speed=2)

        self.enemies.add(e1, e2)

    def _pulse(self, speed=2.0, phase=0.0):
        return 0.5 + 0.5 * math.sin(self.time * speed + phase)

    # ----------------- Events -----------------
    def handle_events(self, events):
        # If player is dead, only accept restart / menu
        if self.player_dead:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        from scenes.ashfall_city import AshfallCityScene
                        self.game.change_scene(AshfallCityScene(self.game))
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

                # Travel to Rift Zone
                if event.key == pygame.K_f and self.gate_active:
                    from scenes.rift_zone import RiftZoneScene
                    self.game.change_scene(RiftZoneScene(self.game))

    # ----------------- Update -----------------
    def update(self, dt):
        self.time += dt
        keys = pygame.key.get_pressed()

        if self.player_dead:
            return

        if self.dialogue and self.dialogue.active:
            return
        if self.echo_dialogue and self.echo_dialogue.active:
            return

        # Update player & enemies
        self.all_sprites.update(keys)
        self.enemies.update()

        # Enemy collisions (damage)
        if self.player.is_alive():
            hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
            if hits:
                self.player.take_damage(15)

        # Check death
        if not self.player.is_alive():
            self.player_dead = True

        # Echo zone logic
        if not self.echo_collected and self.player.rect.colliderect(self.echo_rect):
            self.echo_active = True
        else:
            self.echo_active = False

        if self.echo_active and keys[pygame.K_e] and not self.echo_dialogue:
            self.echo_collected = True
            self.echo_dialogue = DialogueBox(CITY_STREET_ECHO_1)

        # Gate to Rift Zone
        if self.player.rect.colliderect(self.gate_rect):
            self.gate_active = True
        else:
            self.gate_active = False

    # ----------------- Drawing helpers -----------------
    def _draw_city_background(self, surface):
        surface.fill((10, 10, 20))

        # Distant skyline blocks
        skyline_color = (30, 40, 70)
        for i in range(0, settings.WIDTH, 80):
            w = 60
            h = 120 + (i % 3) * 20
            x = i + 10
            y = 120 - (i % 2) * 10
            pygame.draw.rect(surface, skyline_color, (x, y, w, h))

        # Ground
        ground_rect = pygame.Rect(0, settings.HEIGHT // 2 + 40, settings.WIDTH, settings.HEIGHT // 2)
        pygame.draw.rect(surface, (20, 20, 30), ground_rect)

        # Road
        road_rect = pygame.Rect(80, settings.HEIGHT // 2 + 40, settings.WIDTH - 160, 80)
        pygame.draw.rect(surface, (25, 25, 40), road_rect)

        # Road stripes
        stripe_color = (120, 120, 160)
        for x in range(100, settings.WIDTH - 100, 80):
            pygame.draw.rect(surface, stripe_color, (x, road_rect.centery - 4, 40, 8))

        # Cracks / debris
        crack_color = (50, 50, 80)
        pygame.draw.line(surface, crack_color, (120, ground_rect.y + 90), (180, ground_rect.y + 130), 2)
        pygame.draw.line(surface, crack_color, (260, ground_rect.y + 70), (320, ground_rect.y + 110), 2)

        # Gate to Rift Zone (right side)
        gate_color = (80, 0, 100)
        pygame.draw.rect(surface, gate_color, self.gate_rect, border_radius=8)
        inner = self.gate_rect.inflate(-6, -6)
        pygame.draw.rect(surface, (160, 80, 220), inner, 2, border_radius=8)

        ui.draw_text(surface, "RIFT ZONE", 12, (200, 190, 255), self.gate_rect.x - 10, self.gate_rect.y - 18)

    def _draw_echo_zone(self, surface):
        if self.echo_collected:
            return

        pulse = self._pulse(speed=3.0)
        extra = int(4 * pulse)

        glow_surface = pygame.Surface((self.echo_rect.width + 40, self.echo_rect.height + 40), pygame.SRCALPHA)

        pygame.draw.rect(
            glow_surface,
            (settings.COLOR_ECHO[0], settings.COLOR_ECHO[1], settings.COLOR_ECHO[2], 40),
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
            "MEMORY ECHO",
            14,
            settings.COLOR_ECHO,
            self.echo_rect.centerx,
            self.echo_rect.centery - 20,
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
        ui.draw_text(surface, "Echoes of the Last Core // CH-02: ASHFALL CITY", 14, settings.COLOR_TEXT, 20, 10)
        ui.draw_text(surface, "Move: W / A / S / D or Arrow keys", 12, settings.COLOR_TEXT, 20, 32)
        ui.draw_text(surface, "Menu: ESC   ·   Enemies will hurt you on contact", 12, (180, 190, 210), 20, 48)

        objective_pulse = self._pulse(speed=2.0)
        color = (
            160 + int(40 * objective_pulse),
            220,
            255,
        )
        ui.draw_text(
            surface,
            "Objective: Avoid patrols and head towards the Rift Zone gate.",
            14,
            color,
            20,
            70,
        )

        if self.echo_active and not self.echo_collected and not (self.dialogue and self.dialogue.active):
            ui.draw_text(
                surface,
                "Press [E] to trigger a street Memory Echo.",
                14,
                settings.COLOR_HIGHLIGHT,
                20,
                92,
            )

        if self.gate_active and not self.player_dead:
            ui.draw_text(
                surface,
                "Press [F] to enter the Rift Zone.",
                14,
                (200, 190, 255),
                20,
                112,
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
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        ui.draw_centered_text(
            surface,
            "SYSTEM FAILURE",
            32,
            (255, 120, 120),
            settings.WIDTH // 2,
            settings.HEIGHT // 2 - 20,
        )
        ui.draw_centered_text(
            surface,
            "You were overwhelmed by Ashfall patrols.",
            16,
            (220, 200, 210),
            settings.WIDTH // 2,
            settings.HEIGHT // 2 + 10,
        )
        ui.draw_centered_text(
            surface,
            "Press [R] to restart from Ashfall City · Press [ESC] for Main Menu",
            14,
            (200, 200, 220),
            settings.WIDTH // 2,
            settings.HEIGHT // 2 + 40,
        )

    # ----------------- Draw -----------------
    def draw(self, surface):
        self._draw_city_background(surface)
        self._draw_echo_zone(surface)

        self.all_sprites.draw(surface)
        self.enemies.draw(surface)

        self._draw_hud(surface)
        self._draw_death_overlay(surface)

        if self.dialogue and self.dialogue.active:
            self.dialogue.draw(surface)
        elif self.echo_dialogue and self.echo_dialogue.active:
            self.echo_dialogue.draw(surface)
