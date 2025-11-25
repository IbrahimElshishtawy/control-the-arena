# core/scene.py

class Scene:
    """كلاس أساسي لكل المشاهد."""
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass
