# entities/player.py
import pygame
from config import settings

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 32
        self.height = 48
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(settings.COLOR_PLAYER)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 4

    def handle_input(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed

        self.rect.x += dx
        self.rect.y += dy

        self.rect.clamp_ip(pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT))

    def update(self, keys):
        self.handle_input(keys)
