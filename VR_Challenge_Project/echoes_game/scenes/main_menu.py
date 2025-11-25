# scenes/main_menu.py
import pygame
import math
from core.scene import Scene
from core import ui
from config import settings


class MainMenu(Scene):
    def __init__(self, game):
        super().__init__(game)
        # Menu options (English)
        self.options = ["Start Game", "Quit"]
        self.selected = 0

        # Animation timer
        self.time = 0.0

    # -------------------------------------------------------------
    # Event handling
    # -------------------------------------------------------------
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:

                # Navigation
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.options)

                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(self.options)

                # Confirm selection
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.selected == 0:
                        from scenes.lab_scene import LabScene
                        self.game.change_scene(LabScene(self.game))
                    else:
                        self.game.running = False

    def update(self, dt):
        self.time += dt

    # -------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------
    def _pulse(self, speed=2.0, phase=0.0):
        """Returns value between 0 and 1 based on time (for pulsing effects)."""
        return 0.5 + 0.5 * math.sin(self.time * speed + phase)

    # -------------------------------------------------------------
    # Sci-Fi background
    # -------------------------------------------------------------
    def _draw_background(self, surface):
        # Dark base background
        surface.fill((5, 10, 20))

        # Subtle sci-fi grid
        grid_color = (20, 40, 70)
        spacing = 80

        for x in range(0, settings.WIDTH, spacing):
            pygame.draw.line(surface, grid_color, (x, 0), (x, settings.HEIGHT), 1)

        for y in range(0, settings.HEIGHT, spacing):
            pygame.draw.line(surface, grid_color, (0, y), (settings.WIDTH, y), 1)

        # Pulsing circle in the center
        center_x = settings.WIDTH // 2
        center_y = settings.HEIGHT // 2

        pulse_radius = 140 + int(12 * math.sin(self.time * 2))

        pulse_surface = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(
            pulse_surface,
            (
                settings.COLOR_HIGHLIGHT[0],
                settings.COLOR_HIGHLIGHT[1],
                settings.COLOR_HIGHLIGHT[2],
                26,  # alpha
            ),
            (center_x, center_y),
            pulse_radius,
            width=2,
        )
        surface.blit(pulse_surface, (0, 0))

        # Soft vignette
        vignette = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(
            vignette,
            (0, 0, 0, 160),
            (0, 0, settings.WIDTH, settings.HEIGHT),
        )
        vignette.set_alpha(90)
        surface.blit(vignette, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    # -------------------------------------------------------------
    # Hologram menu panel
    # -------------------------------------------------------------
    def _draw_panel(self, surface):
        panel_width = settings.WIDTH - 220
        panel_height = 340
        panel_x = (settings.WIDTH - panel_width) // 2
        panel_y = (settings.HEIGHT - panel_height) // 2

        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)

        # Transparent background
        pygame.draw.rect(
            panel,
            (15, 25, 45, 210),
            (0, 0, panel_width, panel_height),
            border_radius=20,
        )

        # Outer hologram frame
        pygame.draw.rect(
            panel,
            (
                settings.COLOR_HIGHLIGHT[0],
                settings.COLOR_HIGHLIGHT[1],
                settings.COLOR_HIGHLIGHT[2],
                235,
            ),
            (0, 0, panel_width, panel_height),
            width=2,
            border_radius=20,
        )

        # Top decorative line
        pygame.draw.line(
            panel,
            (
                settings.COLOR_HIGHLIGHT[0],
                settings.COLOR_HIGHLIGHT[1],
                settings.COLOR_HIGHLIGHT[2],
                180,
            ),
            (20, 60),
            (panel_width - 20, 60),
            1,
        )

        # Small accent bars in corners
        pygame.draw.line(
            panel,
            (120, 200, 255, 200),
            (24, 24),
            (90, 24),
            3,
        )
        pygame.draw.line(
            panel,
            (120, 200, 255, 200),
            (panel_width - 24, 24),
            (panel_width - 90, 24),
            3,
        )

        surface.blit(panel, (panel_x, panel_y))
        return panel_x, panel_y, panel_width, panel_height

    # -------------------------------------------------------------
    # Small corner labels (professional feel)
    # -------------------------------------------------------------
    def _draw_corner_labels(self, surface):
        # Top-left: section label
        ui.draw_text(
            surface,
            "MAIN MENU",
            14,
            (150, 180, 210),
            20,
            18,
        )

        # Top-right: build info
        build_info = "BUILD: PROTOTYPE 0.1.0"
        info_width = ui.get_font(14).size(build_info)[0]
        ui.draw_text(
            surface,
            build_info,
            14,
            (140, 170, 200),
            settings.WIDTH - info_width - 20,
            18,
        )

        # Bottom-right: fictional copyright / universe detail
        footer = "© 2189 Arkline Systems // Echo Core Project"
        footer_width = ui.get_font(12).size(footer)[0]
        ui.draw_text(
            surface,
            footer,
            12,
            (110, 130, 160),
            settings.WIDTH - footer_width - 20,
            settings.HEIGHT - 24,
        )

    # -------------------------------------------------------------
    # Main draw
    # -------------------------------------------------------------
    def draw(self, surface):
        # Background
        self._draw_background(surface)

        # Hologram panel
        panel_x, panel_y, panel_w, panel_h = self._draw_panel(surface)

        # Title pulsing color
        pulse_value = self._pulse(speed=2.2)
        extra = int(40 * pulse_value)
        title_color = (
            min(255, settings.COLOR_HIGHLIGHT[0] + extra),
            min(255, settings.COLOR_HIGHLIGHT[1] + extra),
            min(255, settings.COLOR_HIGHLIGHT[2] + extra),
        )

        # Glow behind title
        glow_surface = pygame.Surface((panel_w, 80), pygame.SRCALPHA)
        glow_alpha = int(80 + 60 * pulse_value)
        pygame.draw.ellipse(
            glow_surface,
            (
                settings.COLOR_HIGHLIGHT[0],
                settings.COLOR_HIGHLIGHT[1],
                settings.COLOR_HIGHLIGHT[2],
                glow_alpha,
            ),
            (40, 10, panel_w - 80, 60),
        )
        surface.blit(glow_surface, (panel_x, panel_y + 10))

        # Game title
        ui.draw_centered_text(
            surface,
            "ECHOES OF THE LAST CORE",
            34,
            title_color,
            settings.WIDTH // 2,
            panel_y + 40,
        )

        # Subtitle (story hook)
        ui.draw_centered_text(
            surface,
            "Year 2189 · The Central Core went dark. Something is waking up again.",
            16,
            settings.COLOR_TEXT,
            settings.WIDTH // 2,
            panel_y + 78,
        )

        # Additional technical line
        ui.draw_centered_text(
            surface,
            "Python · Pygame · Narrative Prototype · Memory Echo System Online",
            14,
            (175, 190, 220),
            settings.WIDTH // 2,
            panel_y + 104,
        )

        # Animated initialization line
        init_pulse = self._pulse(speed=3.0)
        dots_count = int((self.time * 3) % 4)
        dots = "." * dots_count
        ui.draw_centered_text(
            surface,
            f"INITIALIZING ECHO CORE{dots}",
            14,
            (120 + int(60 * init_pulse), 220, 255),
            settings.WIDTH // 2,
            panel_y + 132,
        )

        # Menu options
        start_y = panel_y + 170

        for i, opt in enumerate(self.options):
            is_selected = (i == self.selected)
            color = settings.COLOR_HIGHLIGHT if is_selected else settings.COLOR_TEXT
            y = start_y + i * 40

            # Side markers for selected option
            if is_selected:
                ui.draw_centered_text(
                    surface,
                    "»",
                    22,
                    settings.COLOR_HIGHLIGHT,
                    settings.WIDTH // 2 - 130,
                    y,
                )
                ui.draw_centered_text(
                    surface,
                    "«",
                    22,
                    settings.COLOR_HIGHLIGHT,
                    settings.WIDTH // 2 + 130,
                    y,
                )

            ui.draw_centered_text(
                surface,
                opt,
                24,
                color,
                settings.WIDTH // 2,
                y,
            )

        # “Press Enter” line pulsing to make start more exciting
        press_pulse = self._pulse(speed=4.0)
        press_color = (
            180 + int(50 * press_pulse),
            200,
            255,
        )
        ui.draw_centered_text(
            surface,
            "PRESS ENTER TO BEGIN SEQUENCE",
            14,
            press_color,
            settings.WIDTH // 2,
            panel_y + panel_h - 52,
        )

        # Input hint
        ui.draw_centered_text(
            surface,
            "W / S or ↑ / ↓ to navigate   ·   Enter to confirm   ·   Esc to exit",
            12,
            (180, 190, 210),
            settings.WIDTH // 2,
            panel_y + panel_h - 28,
        )

        # Corner labels (section, build info, footer)
        self._draw_corner_labels(surface)
