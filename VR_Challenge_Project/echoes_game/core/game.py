# core/game.py
import sys
import pygame

from config import settings

class Game:
    def __init__(self, initial_scene_class):
        pygame.init()
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pygame.display.set_caption(settings.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.current_scene = initial_scene_class(self)

    def change_scene(self, new_scene):
        self.current_scene = new_scene

    def run(self):
        while self.running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.current_scene.handle_events(events)
            self.current_scene.update(dt)
            self.current_scene.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
        sys.exit()
