# scenes/lab_scene.py
import pygame
from core.scene import Scene
from core import ui
from core.dialogue import DialogueBox
from config import settings
from entities.player import Player

class LabScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.player = Player(settings.WIDTH // 2, settings.HEIGHT // 2 + 80)
        self.all_sprites = pygame.sprite.Group(self.player)

        # منطقة الـ Memory Echo
        self.echo_rect = pygame.Rect(
            settings.WIDTH // 2 - 40,
            settings.HEIGHT // 2 - 120,
            80,
            80,
        )
        self.echo_active = False
        self.echo_collected = False

        self.dialogue = DialogueBox(
            [
                "Ryn: ... أين أنا؟ ما الذي حدث هنا؟",
                "Lira: استيقظت أخيراً، المكان انهار بالكامل بعد الانفجار.",
                "Ryn: من أنت؟",
                "Lira: اسمي Lira، مهندسة... وصديقتك الوحيدة الآن إذا أردت الخروج من هنا.",
                "Ryn: أشعر أنني كنت هنا من قبل...",
                "Lira: هذا لأنك كنت جزءاً من فريق حماية النواة قبل الانفجار، لكن ذاكرتك متضررة.",
            ]
        )

        self.echo_dialogue = None

    def handle_events(self, events):
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

    def update(self, dt):
        keys = pygame.key.get_pressed()

        if self.dialogue and self.dialogue.active:
            return
        if self.echo_dialogue and self.echo_dialogue.active:
            return

        self.all_sprites.update(keys)

        if not self.echo_collected and self.player.rect.colliderect(self.echo_rect):
            self.echo_active = True
        else:
            self.echo_active = False

        if self.echo_active and keys[pygame.K_e] and not self.echo_dialogue:
            self.echo_collected = True
            self.echo_dialogue = DialogueBox(
                [
                    "[Memory Echo] (صوت طفل): ابتعدوا! الانفجار سيبدأ خلال ثوانٍ!",
                    "[Memory Echo] (صوت رجل): فعّلوا بروتوكول الطوارئ، لا وقت للتردد!",
                    "Ryn: هذه الأصوات... كنت هنا، في هذه المنشأة، قبل الانفجار.",
                    "Lira: سأحاول فك تشفير ما رأيته الآن، قد يقودنا هذا لمن تسبب في كل شيء.",
                ]
            )

    def draw(self, surface):
        surface.fill(settings.COLOR_BG)

        lab_rect = pygame.Rect(60, 40, settings.WIDTH - 120, settings.HEIGHT - 160)
        pygame.draw.rect(surface, settings.COLOR_LAB_BG, lab_rect)
        pygame.draw.rect(surface, settings.COLOR_LAB_BORDER, lab_rect, 2)

        door_rect = pygame.Rect(settings.WIDTH - 140, settings.HEIGHT // 2 - 50, 40, 100)
        pygame.draw.rect(surface, settings.COLOR_DOOR, door_rect)
        ui.draw_text(surface, "Exit", 14, settings.COLOR_TEXT, door_rect.x - 10, door_rect.y - 20)

        if not self.echo_collected:
            pygame.draw.ellipse(surface, settings.COLOR_ECHO, self.echo_rect, 2)
            ui.draw_centered_text(
                surface,
                "Echo",
                14,
                settings.COLOR_ECHO,
                self.echo_rect.centerx,
                self.echo_rect.centery,
            )

        self.all_sprites.draw(surface)

        ui.draw_text(surface, "WASD / الأسهم للحركة", 14, settings.COLOR_TEXT, 20, 10)
        ui.draw_text(surface, "ESC: رجوع للقائمة", 14, settings.COLOR_TEXT, 20, 30)

        if self.echo_active and not self.echo_collected:
            ui.draw_text(
                surface,
                "اضغط [E] لتفعيل الـ Memory Echo",
                14,
                settings.COLOR_HIGHLIGHT,
                20,
                50,
            )

        if self.dialogue and self.dialogue.active:
            self.dialogue.draw(surface)
        elif self.echo_dialogue and self.echo_dialogue.active:
            self.echo_dialogue.draw(surface)
