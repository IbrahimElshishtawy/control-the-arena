# scenes/ruined_archive.py
import pygame
import math

from core.scene import Scene
from core import ui
from core.dialogue import DialogueBox
from config import settings
from entities.player import Player
from entities.enemy import Enemy
from story.dialogues import (
    ARCHIVE_INTRO_DIALOGUE,
    ARCHIVE_LOG_ECHO_1,
    ARCHIVE_HIDDEN_ECHO,
)


class RuinedArchiveScene(Scene):
    """CH-07: Digital graveyard of failed branches."""

    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.time = 0.0

        self.player = Player(settings.WIDTH // 2, settings.HEIGHT - 120)
        self.all_sprites = pygame.sprite.Group(self.player)

        # A few weak glitch enemies
        self.enemies = pygame.sprite.Group()
        self._spawn_enemies()

        # Echo zones
        self.log_echo_rect = pygame.Rect(
            settings.WIDTH // 2 - 60,
            settings.HEIGHT // 2 + 30,
            120,
            40,
        )
        self.hidden_echo_rect = pygame.Rect(
            140,
            settings.HEIGHT // 2 - 40,
            100,
            40,
        )

        self.log_echo_active = False
        self.hidden_echo_active = False
        self.log_echo_done = False
        self.hidden_echo_done = False

        # Dialogues
        self.intro_dialogue = DialogueBox(ARCHIVE_INTRO_DIALOGUE)
        self.log_echo_dialogue = None
        self.hidden_echo_dialogue = None

        # Gate to next chapter (Mirror Walk)
        self.exit_rect = pygame.Rect(
            settings.WIDTH // 2 - 40,
            60,
            80,
            40,
        )
        self.exit_active = False

        self.player_dead = False

    # ---------------- Helpers ----------------
    def _pulse(self, speed=2.0, phase=0.0):
        return 0.5 + 0.5 * math.sin(self.time * speed + phase)

    def _spawn_enemies(self):
        y = settings.HEIGHT // 2 + 80
        e1 = Enemy(settings.WIDTH // 2 - 150, y, patrol_width=120, speed=1, max_health=40)
        e2 = Enemy(settings.WIDTH // 2 + 140, y, patrol_width=120, speed=1, max_health=40)
        self.enemies.add(e1, e2)

    # ---------------- Events ----------------
    def handle_events(self, events):
        if self.player_dead:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        from scenes.ruined_archive import RuinedArchiveScene
                        self.game.change_scene(RuinedArchiveScene(self.game))
                    elif event.key == pygame.K_ESCAPE:
                        from scenes.main_menu import MainMenu
                        self.game.change_scene(MainMenu(self.game))
            return

        # Dialogues priority
        if self.intro_dialogue and self.intro_dialogue.active:
            for event in events:
                self.intro_dialogue.handle_event(event)
            return

        if self.log_echo_dialogue and self.log_echo_dialogue.active:
            for event in events:
                self.log_echo_dialogue.handle_event(event)
            return

        if self.hidden_echo_dialogue and self.hidden_echo_dialogue.active:
            for event in events:
                self.hidden_echo_dialogue.handle_event(event)
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from scenes.main_menu import MainMenu
                    self.game.change_scene(MainMenu(self.game))

                # Travel to Mirror Walk
                if event.key == pygame.K_f and self.exit_active:
                    from scenes.mirror_walk import MirrorWalkScene
                    self.game.change_scene(MirrorWalkScene(self.game))

                # Trigger log echo
                if event.key == pygame.K_e and self.log_echo_active and not self.log_echo_done:
                    self.log_echo_done = True
                    self.log_echo_dialogue = DialogueBox(ARCHIVE_LOG_ECHO_1)

                # Trigger hidden echo
                if event.key == pygame.K_e and self.hidden_echo_active and not self.hidden_echo_done:
                    self.hidden_echo_done = True
                    self.hidden_echo_dialogue = DialogueBox(ARCHIVE_HIDDEN_ECHO)

    # ---------------- Update ----------------
    def update(self, dt):
        self.time += dt
        keys = pygame.key.get_pressed()

        if self.player_dead:
            return

        if (self.intro_dialogue and self.intro_dialogue.active) or \
           (self.log_echo_dialogue and self.log_echo_dialogue.active) or \
           (self.hidden_echo_dialogue and self.hidden_echo_dialogue.active):
            return

        self.all_sprites.update(keys)
        self.enemies.update()

        # Enemy contact damage (no damage during dash)
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

        if not self.player.is_alive():
            self.player_dead = True

        # Echo zones
        self.log_echo_active = (not self.log_echo_done) and self.player.rect.colliderect(self.log_echo_rect)
        self.hidden_echo_active = (not self.hidden_echo_done) and self.player.rect.colliderect(self.hidden_echo_rect)

        # Exit
        self.exit_active = self.player.rect.colliderect(self.exit_rect)

    # ---------------- Drawing helpers ----------------
    def _draw_background(self, surface):
        surface.fill((4, 6, 16))

        # Floating data fragments (rectangles)
        for i in range(0, settings.WIDTH, 80):
            h = 30 + (i % 3) * 10
            y = 120 + (i * 2) % 140
            pygame.draw.rect(
                surface,
                (20, 40, 80),
                (i + 10, y, 50, h),
                border_radius=8,
            )

        # "Floor" grid
        floor_rect = pygame.Rect(40, settings.HEIGHT // 2 + 40, settings.WIDTH - 80, settings.HEIGHT // 2 - 80)
        pygame.draw.rect(surface, (10, 12, 26), floor_rect)
        for x in range(floor_rect.x, floor_rect.right, 40):
            pygame.draw.line(surface, (25, 28, 50), (x, floor_rect.y), (x, floor_rect.bottom), 1)
        for y in range(floor_rect.y, floor_rect.bottom, 40):
            pygame.draw.line(surface, (25, 28, 50), (floor_rect.x, y), (floor_rect.right, y), 1)

        # Exit portal
        pulse = self._pulse(speed=3.0)
        gate_rect = self.exit_rect.inflate(40, 20)
        pygame.draw.rect(surface, (20, 15, 50), gate_rect, border_radius=10)
        pygame.draw.rect(surface, (140, 180, 255), gate_rect, 2, border_radius=10)

        ui.draw_centered_text(
            surface,
            "MIRROR WALK LINK",
            12,
            (200, 220, 255),
            gate_rect.centerx,
            gate_rect.y - 16,
        )

    def _draw_echo_zone_rect(self, surface, rect, label, active, done):
        if done:
            base_alpha = 40
        else:
            base_alpha = 80

        pulse = self._pulse(speed=3.0)
        extra = int(4 * pulse)

        glow = pygame.Surface((rect.width + 40, rect.height + 40), pygame.SRCALPHA)
        pygame.draw.rect(
            glow,
            (settings.COLOR_ECHO[0], settings.COLOR_ECHO[1], settings.COLOR_ECHO[2], base_alpha),
            glow.get_rect(),
            border_radius=10,
        )
        pygame.draw.rect(
            glow,
            (settings.COLOR_ECHO[0], settings.COLOR_ECHO[1], settings.COLOR_ECHO[2], 160),
            pygame.Rect(10 - extra, 10 - extra, rect.width + extra * 2, rect.height + extra * 2),
            2,
            border_radius=10,
        )
        surface.blit(glow, (rect.x - 20, rect.y - 20))

        pygame.draw.rect(surface, settings.COLOR_ECHO, rect, 2, border_radius=8)
        ui.draw_centered_text(surface, label, 12, settings.COLOR_ECHO, rect.centerx, rect.centery - 18)

        if active and not done:
            ui.draw_centered_text(
                surface,
                "Press [E] to sync this Archive Echo.",
                12,
                (200, 230, 255),
                rect.centerx,
                rect.centery + 20,
            )

    def _draw_health_bar(self, surface):
        ratio = max(0, min(1, self.player.health / self.player.max_health))
        x, y, w, h = 20, settings.HEIGHT - 32, 220, 14
        bg = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, (15, 20, 30), bg, border_radius=6)

        if ratio > 0:
            fg = pygame.Rect(x, y, int(w * ratio), h)
            pygame.draw.rect(surface, (200, 80, 80), fg, border_radius=6)
            glow = pygame.Surface((fg.width, h), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 120, 120, 90), (0, 0, fg.width, h), border_radius=6)
            surface.blit(glow, (x, y))

        pygame.draw.rect(surface, (120, 40, 40), bg, 2, border_radius=6)
        ui.draw_text(surface, "HP", 12, settings.COLOR_TEXT, x - 28, y - 2)

    def _draw_death_overlay(self, surface):
        if not self.player_dead:
            return
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))

        ui.draw_centered_text(
            surface,
            "SIGNAL LOST IN THE ARCHIVE",
            28,
            (255, 160, 180),
            settings.WIDTH // 2,
            settings.HEIGHT // 2 - 10,
        )
        ui.draw_centered_text(
            surface,
            "Press [R] to retry · [ESC] Main Menu",
            14,
            (210, 210, 230),
            settings.WIDTH // 2,
            settings.HEIGHT // 2 + 26,
        )

    def _draw_hud(self, surface):
        ui.draw_text(surface, "Echoes of the Last Core // CH-07: RUINED ARCHIVE", 14, settings.COLOR_TEXT, 20, 10)
        ui.draw_text(surface, "Move: W/A/S/D or Arrows   ·   Combat: J = melee, K = dash", 12, settings.COLOR_TEXT, 20, 32)
        ui.draw_text(surface, "Menu: ESC", 12, (180, 190, 210), 20, 48)

        pulse = self._pulse(speed=2.0)
        color = (160 + int(40 * pulse), 220, 255)
        ui.draw_text(
            surface,
            "Objective: Explore the Archive echoes and head to the Mirror Walk link.",
            14,
            color,
            20,
            70,
        )

        if self.exit_active:
            ui.draw_text(
                surface,
                "Press [F] to travel to the Mirror Walk.",
                13,
                (210, 230, 255),
                20,
                92,
            )

    # ---------------- Draw ----------------
    def draw(self, surface):
        self._draw_background(surface)

        # Echo zones
        self._draw_echo_zone_rect(
            surface,
            self.log_echo_rect,
            "ARCHIVE LOG",
            self.log_echo_active,
            self.log_echo_done,
        )
        self._draw_echo_zone_rect(
            surface,
            self.hidden_echo_rect,
            "HIDDEN SIGNAL",
            self.hidden_echo_active,
            self.hidden_echo_done,
        )

        self.all_sprites.draw(surface)
        self.enemies.draw(surface)

        self._draw_hud(surface)
        self._draw_health_bar(surface)
        self._draw_death_overlay(surface)

        if self.intro_dialogue and self.intro_dialogue.active:
            self.intro_dialogue.draw(surface)
        elif self.log_echo_dialogue and self.log_echo_dialogue.active:
            self.log_echo_dialogue.draw(surface)
        elif self.hidden_echo_dialogue and self.hidden_echo_dialogue.active:
            self.hidden_echo_dialogue.draw(surface)
