# scenes/mirror_walk.py
import pygame
import math

from core.scene import Scene
from core import ui
from core.dialogue import DialogueBox
from config import settings
from entities.player import Player
from entities.enemy import Enemy
from story.dialogues import (
    MIRROR_INTRO_DIALOGUE,
    MIRROR_DUEL_ECHO,
    MIRROR_RESOLUTION_DIALOGUE,
)


class MirrorWalkScene(Scene):
    """CH-08: Corridor of reflective branches and a 'mirror' enemy."""

    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.time = 0.0

        self.player = Player(settings.WIDTH // 2, settings.HEIGHT - 120)
        self.all_sprites = pygame.sprite.Group(self.player)

        # Single tougher enemy representing Mirror Ryn
        self.enemies = pygame.sprite.Group()
        self.mirror_enemy = Enemy(settings.WIDTH // 2, settings.HEIGHT // 2, patrol_width=140, speed=2, max_health=120)
        self.enemies.add(self.mirror_enemy)

        # Echo zone
        self.duel_echo_rect = pygame.Rect(
            settings.WIDTH // 2 - 60,
            settings.HEIGHT // 2 + 60,
            120,
            40,
        )
        self.duel_echo_active = False
        self.duel_echo_done = False

        # Resolution echo (بعد قتل العدو أو تفعيل)
        self.resolution_rect = pygame.Rect(
            settings.WIDTH // 2 - 60,
            120,
            120,
            40,
        )
        self.resolution_active = False
        self.resolution_done = False

        # Dialogues
        self.intro_dialogue = DialogueBox(MIRROR_INTRO_DIALOGUE)
        self.duel_echo_dialogue = None
        self.resolution_dialogue = None

        # Exit to Silent Orbit
        self.exit_rect = pygame.Rect(
            settings.WIDTH // 2 - 40,
            60,
            80,
            30,
        )
        self.exit_active = False

        self.player_dead = False

    def _pulse(self, speed=2.0, phase=0.0):
        return 0.5 + 0.5 * math.sin(self.time * speed + phase)

    # ---------------- Events ----------------
    def handle_events(self, events):
        if self.player_dead:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        from scenes.mirror_walk import MirrorWalkScene
                        self.game.change_scene(MirrorWalkScene(self.game))
                    elif event.key == pygame.K_ESCAPE:
                        from scenes.main_menu import MainMenu
                        self.game.change_scene(MainMenu(self.game))
            return

        if self.intro_dialogue and self.intro_dialogue.active:
            for event in events:
                self.intro_dialogue.handle_event(event)
            return

        if self.duel_echo_dialogue and self.duel_echo_dialogue.active:
            for event in events:
                self.duel_echo_dialogue.handle_event(event)
            return

        if self.resolution_dialogue and self.resolution_dialogue.active:
            for event in events:
                self.resolution_dialogue.handle_event(event)
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from scenes.main_menu import MainMenu
                    self.game.change_scene(MainMenu(self.game))

                # Trigger duel echo (حوار قبل/أثناء القتال)
                if event.key == pygame.K_e and self.duel_echo_active and not self.duel_echo_done:
                    self.duel_echo_done = True
                    self.duel_echo_dialogue = DialogueBox(MIRROR_DUEL_ECHO)

                # Trigger resolution echo (بعد هزيمة العدو)
                if event.key == pygame.K_e and self.resolution_active and not self.resolution_done:
                    self.resolution_done = True
                    self.resolution_dialogue = DialogueBox(MIRROR_RESOLUTION_DIALOGUE)

                # Move to Silent Orbit
                if event.key == pygame.K_f and self.exit_active:
                    from scenes.silent_orbit import SilentOrbitScene
                    self.game.change_scene(SilentOrbitScene(self.game))

    # ---------------- Update ----------------
    def update(self, dt):
        self.time += dt
        keys = pygame.key.get_pressed()

        if self.player_dead:
            return

        if (self.intro_dialogue and self.intro_dialogue.active) or \
           (self.duel_echo_dialogue and self.duel_echo_dialogue.active) or \
           (self.resolution_dialogue and self.resolution_dialogue.active):
            return

        self.all_sprites.update(keys)
        self.enemies.update()

        # Contact damage
        if self.player.is_alive():
            hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
            if hits and not self.player.is_dashing:
                self.player.take_damage(18)

        # Player attack vs mirror enemy
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
        self.duel_echo_active = (not self.duel_echo_done) and self.player.rect.colliderect(self.duel_echo_rect)

        # Resolution zone active فقط بعد موت العدو
        mirror_dead = not self.mirror_enemy.alive()
        self.resolution_active = mirror_dead and (not self.resolution_done) and self.player.rect.colliderect(self.resolution_rect)

        # Exit active بعد حل الـ resolution echo
        self.exit_active = mirror_dead and self.resolution_done and self.player.rect.colliderect(self.exit_rect)

    # ---------------- Drawing helpers ----------------
    def _draw_background(self, surface):
        surface.fill((6, 6, 16))

        # "Mirror" vertical panels
        for x in range(60, settings.WIDTH, 80):
            panel_rect = pygame.Rect(x, 80, 40, settings.HEIGHT - 160)
            pygame.draw.rect(surface, (20, 25, 40), panel_rect)
            pygame.draw.rect(surface, (80, 100, 140), panel_rect, 1)

            # Reflection lines
            pygame.draw.line(surface, (120, 160, 220), (panel_rect.centerx - 4, panel_rect.y + 10),
                             (panel_rect.centerx - 10, panel_rect.bottom - 10), 1)
            pygame.draw.line(surface, (120, 160, 220), (panel_rect.centerx + 4, panel_rect.y + 10),
                             (panel_rect.centerx + 10, panel_rect.bottom - 10), 1)

        # Exit door
        gate_rect = self.exit_rect.inflate(40, 14)
        pygame.draw.rect(surface, (22, 26, 50), gate_rect, border_radius=8)
        pygame.draw.rect(surface, (180, 210, 255), gate_rect, 2, border_radius=8)

        ui.draw_centered_text(
            surface,
            "TO SILENT ORBIT",
            12,
            (210, 220, 255),
            gate_rect.centerx,
            gate_rect.y - 16,
        )

    def _draw_echo_rect(self, surface, rect, label, active, done):
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
            "MIRROR WALK FAILED",
            28,
            (255, 150, 180),
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
        ui.draw_text(surface, "Echoes of the Last Core // CH-08: MIRROR WALK", 14, settings.COLOR_TEXT, 20, 10)
        ui.draw_text(surface, "Move: W/A/S/D or Arrows   ·   Combat: J = melee, K = dash", 12, settings.COLOR_TEXT, 20, 32)
        ui.draw_text(surface, "Menu: ESC", 12, (180, 190, 210), 20, 48)

        pulse = self._pulse(2.0)
        color = (160 + int(40 * pulse), 220, 255)
        ui.draw_text(
            surface,
            "Objective: Face your mirror self and stabilize your signal.",
            14,
            color,
            20,
            70,
        )

        if self.exit_active:
            ui.draw_text(
                surface,
                "Press [F] to travel to the Silent Orbit.",
                13,
                (210, 230, 255),
                20,
                92,
            )

    # ---------------- Draw ----------------
    def draw(self, surface):
        self._draw_background(surface)

        self._draw_echo_rect(
            surface,
            self.duel_echo_rect,
            "MIRROR ECHO",
            self.duel_echo_active,
            self.duel_echo_done,
        )

        self._draw_echo_rect(
            surface,
            self.resolution_rect,
            "ALIGNMENT ECHO",
            self.resolution_active,
            self.resolution_done,
        )

        self.all_sprites.draw(surface)
        self.enemies.draw(surface)

        self._draw_hud(surface)
        self._draw_health_bar(surface)
        self._draw_death_overlay(surface)

        if self.intro_dialogue and self.intro_dialogue.active:
            self.intro_dialogue.draw(surface)
        elif self.duel_echo_dialogue and self.duel_echo_dialogue.active:
            self.duel_echo_dialogue.draw(surface)
        elif self.resolution_dialogue and self.resolution_dialogue.active:
            self.resolution_dialogue.draw(surface)
