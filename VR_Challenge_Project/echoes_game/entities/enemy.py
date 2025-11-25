# entities/enemy.py
import pygame
from config import settings


class Enemy(pygame.sprite.Sprite):
    """
    Simple patrolling enemy for Ashfall City.
    Walks left/right along the road and damages the player on contact.
    """

    def __init__(self, x, y, patrol_width=160, speed=2):
        super().__init__()

        self.width = 32
        self.height = 48

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

        self.speed = speed
        self.patrol_width = patrol_width
        self.start_x = x
        self.direction = 1  # 1 → right, -1 → left

        self._draw_enemy()

    def _draw_enemy(self):
        """Draw simple hostile robot / soldier style."""
        surf = self.image
        surf.fill((0, 0, 0, 0))

        w, h = self.width, self.height

        # Body
        body_rect = pygame.Rect(w // 4, h // 4, w // 2, h // 2)
        pygame.draw.rect(surf, (170, 60, 70), body_rect, border_radius=6)
        pygame.draw.rect(surf, (40, 10, 20), body_rect, 2, border_radius=6)

        # Head
        head_rect = pygame.Rect(w // 4, h // 8, w // 2, h // 5)
        pygame.draw.rect(surf, (220, 80, 90), head_rect, border_radius=4)
        pygame.draw.rect(surf, (40, 10, 20), head_rect, 2, border_radius=4)

        # "Eyes"
        eye_rect = pygame.Rect(head_rect.x + 4, head_rect.y + 4, head_rect.width - 8, head_rect.height - 8)
        pygame.draw.rect(surf, (255, 220, 120), eye_rect, border_radius=3)

        # Legs
        leg_w = w // 4
        leg_h = h // 4
        left_leg = pygame.Rect(w // 4, body_rect.bottom, leg_w, leg_h)
        right_leg = pygame.Rect(w // 2, body_rect.bottom, leg_w, leg_h)
        pygame.draw.rect(surf, (120, 40, 50), left_leg, border_radius=4)
        pygame.draw.rect(surf, (120, 40, 50), right_leg, border_radius=4)

    def update(self):
        # Patrol horizontally around start_x
        self.rect.x += self.speed * self.direction

        if self.rect.x < self.start_x - self.patrol_width // 2:
            self.rect.x = self.start_x - self.patrol_width // 2
            self.direction = 1
        elif self.rect.x > self.start_x + self.patrol_width // 2:
            self.rect.x = self.start_x + self.patrol_width // 2
            self.direction = -1

        # Keep inside screen vertically just in case
        self.rect.clamp_ip(pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT))
