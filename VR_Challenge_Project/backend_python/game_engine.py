import time
from dataclasses import dataclass, asdict, field
from typing import List


# ========= إعدادات بسيطة للعبة ========= #

ARENA_WIDTH = 800
ARENA_HEIGHT = 400

PLAYER_MOVE_SPEED = 200.0      # بيكسل في الثانية
PLAYER_JUMP_VELOCITY = 300.0   # سرعة القفز الأولية
GRAVITY = 600.0                # جاذبية للأسفل

BULLET_SPEED = 400.0           # سرعة الرصاصة
BULLET_LIFETIME = 2.0          # ثواني

ENEMY_SPEED = 80.0             # سرعة العدو
ENEMY_SPAWN_INTERVAL = 3.0     # كل كام ثانية يطلع عدو جديد
ENEMY_DAMAGE = 10              # ضرر العدو للاعب
BULLET_DAMAGE = 50             # ضرر الرصاصة للعدو

PLAYER_HITBOX = 30             # حجم صندوق التصادم للاعب
ENEMY_HITBOX = 30
BULLET_HITBOX = 10


# ========= Data Classes ========= #

@dataclass
class PlayerState:
    x: float = 100.0
    y: float = 0.0
    hp: int = 100
    on_ground: bool = True
    vertical_velocity: float = 0.0


@dataclass
class BulletState:
    x: float
    y: float
    direction: int = 1  # 1 يمين, -1 شمال
    created_at: float = field(default_factory=time.time)
    active: bool = True


@dataclass
class EnemyState:
    x: float
    y: float
    hp: int = 100
    speed: float = ENEMY_SPEED
    alive: bool = True


@dataclass
class GameState:
    score: int = 0
    level: int = 1
    player: PlayerState = field(default_factory=PlayerState)
    is_game_over: bool = False

    enemies_count: int = 0
    bullets_count: int = 0

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "level": self.level,
            "player": asdict(self.player),
            "is_game_over": self.is_game_over,
            "enemies_count": self.enemies_count,
            "bullets_count": self.bullets_count,
        }


# ========= محرك اللعبة ========= #

class GameEngine:
    """
    مسئول عن الـ Game Logic الأساسي:
    - حركة اللاعب + القفز
    - الرصاص
    - الأعداء
    - التصادمات
    - حساب Score / HP / Level
    """

    def __init__(self):
        self.state = GameState()
        self.last_update = time.time()

        self.bullets: List[BulletState] = []
        self.enemies: List[EnemyState] = []

        self._time_since_last_spawn = 0.0

    # ----- مدخلات من Flutter -----

    def handle_input(self, action: str):
        """
        تستدعى من websocket_server لما يجي أمر من الموبايل.
        """
        if self.state.is_game_over:
            # ممكن تضيف reset هنا بعدين لو حابب
            return

        if action == "move_left":
            self._move_player(horizontal_dir=-1)
        elif action == "move_right":
            self._move_player(horizontal_dir=1)
        elif action == "jump":
            self._player_jump()
        elif action == "shoot":
            self._player_shoot()

    # ----- منطق الحركة -----

    def _move_player(self, horizontal_dir: int):
        """
        تحريك اللاعب يمين/شمال بناءً على dir = -1 أو 1
        """
        now = time.time()
        delta = now - self.last_update
        # هنا الحركة فورية بسيطة, ممكن تتحسن بعدين
        dx = PLAYER_MOVE_SPEED * delta * horizontal_dir
        self.state.player.x += dx

        # حدود الساحة
        self.state.player.x = max(0, min(ARENA_WIDTH, self.state.player.x))

    def _player_jump(self):
        if self.state.player.on_ground:
            self.state.player.on_ground = False
            self.state.player.vertical_velocity = PLAYER_JUMP_VELOCITY

    def _player_shoot(self):
        bullet = BulletState(
            x=self.state.player.x + 20,  # قدام اللاعب شوية
            y=self.state.player.y + 20,
            direction=1,  # حالياً نرمي يمين بس
        )
        self.bullets.append(bullet)

    # ----- update loop -----

    def update(self):
        """
        تستدعى كل مرة بعد handle_input أو بشكل دوري.
        """
        now = time.time()
        delta = now - self.last_update
        self.last_update = now

        if self.state.is_game_over:
            return

        # جاذبية + قفز
        self._update_player_physics(delta)

        # تحديث الرصاص
        self._update_bullets(delta, now)

        # توليد أعداء وتحديث حركتهم
        self._update_enemies(delta)

        # تصادمات
        self._handle_collisions()

        # تحديث أرقام level/enemy/bullets
        self._update_meta_state()

    def _update_player_physics(self, delta: float):
        if not self.state.player.on_ground:
            # تطبيق الجاذبية
            self.state.player.vertical_velocity -= GRAVITY * delta
            self.state.player.y += self.state.player.vertical_velocity * delta

            # رجوع للأرض
            if self.state.player.y <= 0:
                self.state.player.y = 0
                self.state.player.vertical_velocity = 0.0
                self.state.player.on_ground = True

        # ممكن تضيف حدود ارتفاع max لو حبيت

    def _update_bullets(self, delta: float, now: float):
        for bullet in self.bullets:
            if not bullet.active:
                continue

            # حركة الرصاصة
            bullet.x += BULLET_SPEED * delta * bullet.direction

            # انتهاء عمر الرصاصة
            if now - bullet.created_at > BULLET_LIFETIME:
                bullet.active = False

            # خروج من حدود الساحة
            if bullet.x < 0 or bullet.x > ARENA_WIDTH:
                bullet.active = False

        # تنظيف الرصاص غير النشط
        self.bullets = [b for b in self.bullets if b.active]

    def _spawn_enemy(self):
        # عدو جديد من اليمين متجه لليسار
        enemy = EnemyState(
            x=ARENA_WIDTH + 50,
            y=0,
            hp=100,
            speed=ENEMY_SPEED,
        )
        self.enemies.append(enemy)

    def _update_enemies(self, delta: float):
        # توليد أعداء
        self._time_since_last_spawn += delta
        if self._time_since_last_spawn >= ENEMY_SPAWN_INTERVAL:
            self._spawn_enemy()
            self._time_since_last_spawn = 0.0

        # حركة الأعداء
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            # يتحرك ناحية اللاعب (بسيطة: من اليمين للشمال)
            enemy.x -= enemy.speed * delta

            # لو خرج بره الشاشة من الشمال, نعتبره مات
            if enemy.x < -100:
                enemy.alive = False

        # تنظيف الأعداء الميتين
        self.enemies = [e for e in self.enemies if e.alive]

    # ----- التصادمات -----

    def _handle_collisions(self):
        player = self.state.player

        # Bullet vs Enemy
        for bullet in self.bullets:
            if not bullet.active:
                continue

            for enemy in self.enemies:
                if not enemy.alive:
                    continue

                if self._check_collision(
                    bullet.x,
                    bullet.y,
                    BULLET_HITBOX,
                    enemy.x,
                    enemy.y,
                    ENEMY_HITBOX,
                ):
                    bullet.active = False
                    enemy.hp -= BULLET_DAMAGE
                    if enemy.hp <= 0:
                        enemy.alive = False
                        self.state.score += 10

        # Enemy vs Player
        for enemy in self.enemies:
            if not enemy.alive:
                continue

            if self._check_collision(
                player.x,
                player.y,
                PLAYER_HITBOX,
                enemy.x,
                enemy.y,
                ENEMY_HITBOX,
            ):
                enemy.alive = False  # اعتبر العدو اختفى بعد ما خبطك
                player.hp -= ENEMY_DAMAGE
                if player.hp <= 0:
                    player.hp = 0
                    self.state.is_game_over = True

        # بعد التصادمات, نظف lists
        self.bullets = [b for b in self.bullets if b.active]
        self.enemies = [e for e in self.enemies if e.alive]

    @staticmethod
    def _check_collision(x1: float, y1: float, r1: float,
                         x2: float, y2: float, r2: float) -> bool:
        """
        تصادم دائري بسيط (مسافة بين المركزين أقل من مجموع الأنصاف)
        """
        dx = x1 - x2
        dy = y1 - y2
        dist_sq = dx * dx + dy * dy
        radius_sum = r1 + r2
        return dist_sq <= radius_sum * radius_sum

    # ----- meta state -----

    def _update_meta_state(self):
        self.state.enemies_count = len(self.enemies)
        self.state.bullets_count = len(self.bullets)

        # Level بسيط بناء على الـ score
        if self.state.score >= 50:
            self.state.level = 3
        elif self.state.score >= 20:
            self.state.level = 2
        else:
            self.state.level = 1

    # ----- API للسيرفر -----

    def get_state_dict(self) -> dict:
        """
        يستدعيها websocket_server.py عشان يبعث حالة اللعبة لـ Flutter.
        """
        return self.state.to_dict()
