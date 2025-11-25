# core/ui.py
import pygame

def get_font(size: int):
    """إرجاع فونت بالحجم المطلوب."""
    return pygame.font.SysFont("consolas", size)

def draw_text(surface, text, size, color, x, y):
    font = get_font(size)
    img = font.render(text, True, color)
    surface.blit(img, (x, y))

def draw_centered_text(surface, text, size, color, center_x, center_y):
    font = get_font(size)
    img = font.render(text, True, color)
    rect = img.get_rect(center=(center_x, center_y))
    surface.blit(img, rect)
