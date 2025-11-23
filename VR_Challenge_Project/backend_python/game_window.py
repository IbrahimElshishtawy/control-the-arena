import pygame
import time

from game_engine import GameEngine, ARENA_WIDTH, ARENA_HEIGHT

# ألوان بسيطة
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (0, 150, 255)
ENEMY_COLOR = (255, 70, 70)
BULLET_COLOR = (255, 255, 0)


def main():
    pygame.init()
    screen = pygame.display.set_mode((ARENA_WIDTH, ARENA_HEIGHT))
    pygame.display.set_caption("Control The Arena - Python Render")

    clock = pygame.time.Clock()
    engine = GameEngine()

    running = True
    last_time = time.time()

    while running:
        delta = clock.tick(60) / 1000.0


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # تحديث اللعبة (Player + Enemies + Bullets)
        engine.update()

        # رسم الخلفية
        screen.fill(BLACK)

        # رسم اللاعب
        px = int(engine.state.player.x)
        py = ARENA_HEIGHT - int(engine.state.player.y) - 40
        pygame.draw.rect(screen, PLAYER_COLOR, (px, py, 40, 40)) 

        # رسم الأعداء
        for enemy in engine.enemies:
            ex = int(enemy.x)
            ey = ARENA_HEIGHT - int(enemy.y) - 40
            pygame.draw.rect(screen, ENEMY_COLOR, (ex, ey, 40, 40))

        # رسم الرصاص
        for bullet in engine.bullets:
            bx = int(bullet.x)
            by = ARENA_HEIGHT - int(bullet.y) - 15
            pygame.draw.circle(screen, BULLET_COLOR, (bx, by), 5)

        # عرض Score و HP
        font = pygame.font.SysFont(None, 30)
        text = font.render(
            f"Score: {engine.state.score}   HP: {engine.state.player.hp}",
            True, WHITE
        )
        screen.blit(text, (10, 10))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
