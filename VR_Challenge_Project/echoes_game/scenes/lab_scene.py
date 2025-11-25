# scenes/lab_scene.py
import pygame
import math

from core.scene import Scene
from core import ui
from core.dialogue import DialogueBox
from config import settings
from entities.player import Player
from story.dialogues import LAB_INTRO_DIALOGUE, LAB_ECHO_1_DIALOGUE


class LabScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.game = game
        self.time = 0.0

        # Intro / cinematic sequence
        self.intro_time = 0.0
        self.intro_duration = 4.0   # seconds before player can move
        self.in_intro = True

        # Player
        self.player = Player(settings.WIDTH // 2, settings.HEIGHT // 2 + 80)
        self.all_sprites = pygame.sprite.Group(self.player)

        # Memory Echo area
        self.echo_rect = pygame.Rect(
            settings.WIDTH // 2 - 40,
            settings.HEIGHT // 2 - 120,
            80,
            80,
        )
        self.echo_active = False
        self.echo_collected = False

        # Intro dialogue (English) – now from story.dialogues
        self.dialogue = DialogueBox(LAB_INTRO_DIALOGUE)

        # Memory Echo dialogue (appears after pressing E inside the Echo area)
        self.echo_dialogue = None

        # Lab layout rect
        self.lab_rect = pygame.Rect(60, 40, settings.WIDTH - 120, settings.HEIGHT - 160)

        # Door rect (exit)
        self.door_rect = pygame.Rect(settings.WIDTH - 140, settings.HEIGHT // 2 - 50, 40, 100)
        self.door_active = False  # هل اللاعب قرب الباب؟

    # -------------------------------------------------------------
    # Helper for pulsing values
    # -------------------------------------------------------------
    def _pulse(self, speed=2.0, phase=0.0):
        """Return value between 0 and 1 for pulsing animations."""
        return 0.5 + 0.5 * math.sin(self.time * speed + phase)

    # -------------------------------------------------------------
    # Event handling
    # -------------------------------------------------------------
    def handle_events(self, events):
        # While any dialogue is active, only feed events to it
        if self.dialogue and self.dialogue.active:
            for event in events:
                self.dialogue.handle_event(event)
            return

        if self.echo_dialogue and self.echo_dialogue.active:
            for event in events:
                self.echo_dialogue.handle_event(event)
            return

        # Normal input (after dialogues)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from scenes.main_menu import MainMenu
                    self.game.change_scene(MainMenu(self.game))

                # انتقال للفصل الثاني عند الباب
                if event.key == pygame.K_f and self.door_active:
                    from scenes.ashfall_city import AshfallCityScene
                    self.game.change_scene(AshfallCityScene(self.game))

    # -------------------------------------------------------------
    # Update
    # -------------------------------------------------------------
    def update(self, dt):
        # Always advance time for animations
        self.time += dt
        self.intro_time += dt

        # After intro_duration seconds, we end the cinematic intro
        if self.intro_time >= self.intro_duration:
            self.in_intro = False

        keys = pygame.key.get_pressed()

        # Stop movement while dialogues are active
        if self.dialogue and self.dialogue.active:
            return
        if self.echo_dialogue and self.echo_dialogue.active:
            return

        # Stop movement while intro cinematic is running
        if self.in_intro:
            return

        # Update player movement
        self.all_sprites.update(keys)

        # Check Echo activation zone
        if not self.echo_collected and self.player.rect.colliderect(self.echo_rect):
            self.echo_active = True
        else:
            self.echo_active = False

        # Check door activation zone
        if self.player.rect.colliderect(self.door_rect):
            self.door_active = True
        else:
            self.door_active = False

        # Trigger Memory Echo
        if self.echo_active and keys[pygame.K_e] and not self.echo_dialogue:
            self.echo_collected = True
            self.echo_dialogue = DialogueBox(LAB_ECHO_1_DIALOGUE)

    # -------------------------------------------------------------
    # Drawing helpers
    # -------------------------------------------------------------
    def _draw_lab_background(self, surface):
        # Base background
        surface.fill(settings.COLOR_BG)

        # Main lab room
        pygame.draw.rect(surface, settings.COLOR_LAB_BG, self.lab_rect)
        pygame.draw.rect(surface, settings.COLOR_LAB_BORDER, self.lab_rect, 2)

        # Vertical light panels on the walls
        left_panel = pygame.Rect(self.lab_rect.x + 12, self.lab_rect.y + 20, 8, self.lab_rect.height - 40)
        right_panel = pygame.Rect(self.lab_rect.right - 20, self.lab_rect.y + 20, 8, self.lab_rect.height - 40)

        pygame.draw.rect(surface, (40, 90, 140), left_panel)
        pygame.draw.rect(surface, (40, 90, 140), right_panel)

        # Floor grid
        grid_color = (35, 50, 80)
        spacing = 40
        for x in range(self.lab_rect.x + 20, self.lab_rect.right - 20, spacing):
            pygame.draw.line(surface, grid_color, (x, self.lab_rect.y + 40), (x, self.lab_rect.bottom - 20), 1)
        for y in range(self.lab_rect.y + 40, self.lab_rect.bottom - 20, spacing):
            pygame.draw.line(surface, grid_color, (self.lab_rect.x + 20, y), (self.lab_rect.right - 20, y), 1)

    def _draw_door(self, surface):
        # Door body
        pygame.draw.rect(surface, settings.COLOR_DOOR, self.door_rect, border_radius=6)

        # Door inner frame
        inner = self.door_rect.inflate(-6, -6)
        pygame.draw.rect(surface, (130, 140, 190), inner, 2, border_radius=6)

        # Door label
        ui.draw_text(surface, "EXIT", 14, settings.COLOR_TEXT, self.door_rect.x - 4, self.door_rect.y - 22)
        ui.draw_text(surface, "TO ASHFALL CITY", 10, (170, 190, 230), self.door_rect.x - 24, self.door_rect.y - 10)

        # Small indicator light on the door
        light_radius = 4
        light_center = (self.door_rect.centerx, self.door_rect.y + 12)
        pulse = self._pulse(speed=4.0)
        color = (120 + int(80 * pulse), 220, 150)
        pygame.draw.circle(surface, (20, 40, 30), light_center, light_radius + 2)
        pygame.draw.circle(surface, color, light_center, light_radius)

        # Hint for interaction near door
        if self.door_active:
            ui.draw_text(surface, "[F] Travel to Ashfall City", 14, settings.COLOR_HIGHLIGHT,
                         self.door_rect.x - 80, self.door_rect.y + self.door_rect.height + 8)

    def _draw_echo_zone(self, surface):
        if self.echo_collected:
            return

        # Pulsing ring around Echo area
        pulse = self._pulse(speed=3.0)
        extra_radius = int(8 * pulse)

        glow_surface = pygame.Surface((self.echo_rect.width + 40, self.echo_rect.height + 40), pygame.SRCALPHA)

        # Outer glow
        pygame.draw.ellipse(
            glow_surface,
            (settings.COLOR_ECHO[0], settings.COLOR_ECHO[1], settings.COLOR_ECHO[2], 40),
            glow_surface.get_rect(),
        )

        # Inner pulsing ring
        pygame.draw.ellipse(
            glow_surface,
            (settings.COLOR_ECHO[0], settings.COLOR_ECHO[1], settings.COLOR_ECHO[2], 160),
            pygame.Rect(
                10 - extra_radius,
                10 - extra_radius,
                self.echo_rect.width + extra_radius * 2,
                self.echo_rect.height + extra_radius * 2,
            ),
            2,
        )

        surface.blit(glow_surface, (self.echo_rect.x - 20, self.echo_rect.y - 20))

        # Base ellipse outline
        pygame.draw.ellipse(surface, settings.COLOR_ECHO, self.echo_rect, 2)

        # Echo label
        ui.draw_centered_text(
            surface,
            "MEMORY ECHO",
            14,
            settings.COLOR_ECHO,
            self.echo_rect.centerx,
            self.echo_rect.centery,
        )

    def _draw_hud(self, surface):
        # Header
        ui.draw_text(surface, "Echoes of the Last Core // LAB-01: COLLAPSED FACILITY", 14, settings.COLOR_TEXT, 20, 10)

        # Controls
        ui.draw_text(surface, "Move: W / A / S / D or Arrow keys", 12, settings.COLOR_TEXT, 20, 32)
        ui.draw_text(surface, "Menu: ESC", 12, (180, 190, 210), 20, 48)

        # Objective
        objective_pulse = self._pulse(speed=2.5)
        color = (
            160 + int(40 * objective_pulse),
            220,
            255,
        )
        ui.draw_text(
            surface,
            "Objective: Reach the exit door.",
            14,
            color,
            20,
            70,
        )

        # Hint for Echo
        if self.echo_active and not self.echo_collected and not (self.dialogue and self.dialogue.active):
            ui.draw_text(
                surface,
                "Press [E] to activate Memory Echo.",
                14,
                settings.COLOR_HIGHLIGHT,
                20,
                92,
            )

    def _draw_alarm_overlay(self, surface):
        """Red alarm flash during intro to make it more dramatic."""
        if self.in_intro:
            strength = self._pulse(speed=5.0)
            alpha = int(90 * strength)
            alarm_surface = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            alarm_surface.fill((255, 60, 60, alpha))
            surface.blit(alarm_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # -------------------------------------------------------------
    # Draw
    # -------------------------------------------------------------
    def draw(self, surface):
        # We draw the whole world to an off-screen surface, then apply camera shake
        world_surface = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)

        # Background + lab structure
        self._draw_lab_background(world_surface)

        # Echo zone
        self._draw_echo_zone(world_surface)

        # Door
        self._draw_door(world_surface)

        # Player
        self.all_sprites.draw(world_surface)

        # HUD / instructions
        self._draw_hud(world_surface)

        # Alarm overlay (intro)
        self._draw_alarm_overlay(world_surface)

        # Camera shake during intro
        if self.in_intro:
            # Intensity fades with intro time
            t = max(0.0, self.intro_duration - self.intro_time) / self.intro_duration
            intensity = 6 * t
            shake_x = int(math.sin(self.time * 25) * intensity)
            shake_y = int(math.cos(self.time * 22) * intensity)
        else:
            shake_x = 0
            shake_y = 0

        # Blit world with shake offset
        surface.blit(world_surface, (shake_x, shake_y))

        # Dialogues overlays (kept stable on screen, not shaking)
        if self.dialogue and self.dialogue.active:
            self.dialogue.draw(surface)
        elif self.echo_dialogue and self.echo_dialogue.active:
            self.echo_dialogue.draw(surface)
