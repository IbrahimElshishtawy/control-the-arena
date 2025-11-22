import time
from dataclasses import dataclass, asdict


@dataclass
class PlayerState:
  x: int = 0
  y: int = 0
  hp: int = 100


@dataclass
class GameState:
  score: int = 0
  level: int = 1
  player: PlayerState = PlayerState()
  is_game_over: bool = False

  def to_dict(self) -> dict:
    return {
      "score": self.score,
      "level": self.level,
      "player": asdict(self.player),
      "is_game_over": self.is_game_over,
    }


class GameEngine:
  """
  مسئول عن الـ Game Logic الأساسي.
  حالياً منطق بسيط جداً للتجارب الأولى.
  """

  def __init__(self):
    self.state = GameState()
    self.last_update = time.time()

  def handle_input(self, action: str):
    # هنا تكتب منطق رد الفعل على أوامر الكنترولر
    if action == "move_left":
      self.state.player.x -= 5
    elif action == "move_right":
      self.state.player.x += 5
    elif action == "jump":
      self.state.player.y += 10
    elif action == "shoot":
      self.state.score += 10

    # مثال بسيط لو الـ hp وصل للصفر
    if self.state.player.hp <= 0:
      self.state.is_game_over = True

  def update(self):
    """
    تستدعيها كل شوية عشان تحدث فيزياء / زمن / إلخ.
    حالياً: تنزيل اللاعب بعد الـ jump.
    """
    now = time.time()
    delta = now - self.last_update
    self.last_update = now

    # مثال بسيط يرجّع اللاعب للأرض
    if self.state.player.y > 0:
      self.state.player.y -= int(20 * delta)
      if self.state.player.y < 0:
        self.state.player.y = 0

  def get_state_dict(self) -> dict:
    return self.state.to_dict()
