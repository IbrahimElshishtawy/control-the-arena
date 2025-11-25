# entities/player.py
import pygame
from config import settings


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # حجم الشخصية
        self.width = 40
        self.height = 64

        # سطح مع شفافية
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

        self.speed = 4
        self.facing = "down"

        # رسم أولي
        self._draw_idle()

    # ---------------- رسم الرأس / الخوذة ----------------
    def _draw_head(self, surf):
        w, h = self.width, self.height

        head_radius = w // 4
        head_center = (w // 2, head_radius + 4)

        # سطح منفصل للرأس لسهولة التحكم
        head_size = head_radius * 2 + 8
        head_surf = pygame.Surface((head_size, head_size), pygame.SRCALPHA)
        cx, cy = head_size // 2, head_size // 2

        # خوذة أساسية
        pygame.draw.circle(head_surf, settings.COLOR_PLAYER_SUIT, (cx, cy), head_radius)
        pygame.draw.circle(head_surf, settings.COLOR_PLAYER_OUTLINE, (cx, cy), head_radius, 2)

        # visor (زجاج أمامي) بيضاوي
        visor_w = int(head_radius * 1.5)
        visor_h = int(head_radius * 0.9)
        visor_rect = pygame.Rect(0, 0, visor_w, visor_h)
        visor_rect.center = (cx, cy + 2)

        # طبقة مظلمة داخلية
        pygame.draw.ellipse(head_surf, settings.COLOR_PLAYER_VISOR_DARK, visor_rect)

        # طبقة الزجاج الأساسية
        inner_visor = visor_rect.inflate(-4, -4)
        pygame.draw.ellipse(head_surf, settings.COLOR_PLAYER_VISOR, inner_visor)
        pygame.draw.ellipse(head_surf, settings.COLOR_PLAYER_OUTLINE, inner_visor, 2)

        # ظل سفلي (يعطي عمق)
        shadow_rect = inner_visor.copy()
        shadow_rect.y += shadow_rect.height // 3
        shadow_rect.height //= 2
        shadow_surf = pygame.Surface((head_size, head_size), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 70), shadow_rect)
        head_surf.blit(shadow_surf, (0, 0))

        # لمعة مائلة (هايلايت)
        hl_rect = pygame.Rect(0, 0, visor_w // 2, visor_h // 3)
        hl_rect.center = (cx - visor_w // 4, cy - visor_h // 4)
        hl_surf = pygame.Surface((head_size, head_size), pygame.SRCALPHA)
        pygame.draw.ellipse(hl_surf, settings.COLOR_PLAYER_VISOR_LIGHT, hl_rect)
        hl_surf.set_alpha(170)
        head_surf.blit(hl_surf, (0, 0))

        # توهج خفيف في الأسفل
        glow_rect = pygame.Rect(0, 0, visor_w // 3, visor_h // 3)
        glow_rect.center = (cx + visor_w // 4, cy + visor_h // 6)
        glow_surf = pygame.Surface((head_size, head_size), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, settings.COLOR_PLAYER_VISOR_GLOW, glow_rect)
        glow_surf.set_alpha(80)
        head_surf.blit(glow_surf, (0, 0))

        # “ذقن” أو فلتر
        chin_w = int(head_radius * 1.1)
        chin_h = head_radius // 3
        chin_rect = pygame.Rect(0, 0, chin_w, chin_h)
        chin_rect.center = (cx, cy + head_radius // 1.3)
        pygame.draw.rect(head_surf, settings.COLOR_PLAYER_OUTLINE, chin_rect, border_radius=6)
        inner_chin = chin_rect.inflate(-4, -4)
        pygame.draw.rect(head_surf, (20, 60, 50), inner_chin, border_radius=6)

        # وضع الرأس على الـ surf الأساسي
        dest_x = head_center[0] - head_size // 2
        dest_y = head_center[1] - head_size // 2
        surf.blit(head_surf, (dest_x, dest_y))

    # ---------------- جسم 3D-Style (Top / Front / Side) ----------------
    def _draw_body_3d(self, surf):
        """
        جسم بشكل بريسم شبه 3D (isometric-style):
        - وجه علوي (TOP) لون فاتح
        - وجه أمامي (FRONT) أغمق
        - وجه جانبي (SIDE) متوسط
        """

        w, h = self.width, self.height

        head_radius = w // 4
        head_center_y = head_radius + 4

        body_width = int(w * 0.6)
        body_height = int(h * 0.42)

        body_x = (w - body_width) // 2
        body_y = head_center_y + head_radius - 2

        # offset عمق للـ 3D
        depth = 6

        # نقاط الوجه العلوي (Top) كـ شكل مائل قليلاً
        top_front_y = body_y
        top_back_y = body_y - depth

        top_left_x = body_x
        top_right_x = body_x + body_width

        top_polygon = [
            (top_left_x, top_front_y),
            (top_right_x, top_front_y),
            (top_right_x - depth, top_back_y),
            (top_left_x + depth, top_back_y),
        ]

        pygame.draw.polygon(surf, settings.COLOR_PLAYER_SUIT_TOP, top_polygon)
        pygame.draw.polygon(surf, settings.COLOR_PLAYER_OUTLINE, top_polygon, 2)

        # الوجه الأمامي (Front)
        front_rect = pygame.Rect(
            body_x,
            body_y,
            body_width,
            body_height,
        )
        pygame.draw.rect(
            surf,
            settings.COLOR_PLAYER_SUIT_FRONT,
            front_rect,
            border_radius=8,
        )
        pygame.draw.rect(
            surf,
            settings.COLOR_PLAYER_OUTLINE,
            front_rect,
            2,
            border_radius=8,
        )

        # الوجه الجانبي (Side) على اليمين
        side_polygon = [
            (front_rect.right, front_rect.top),                # أعلى أمام يمين
            (front_rect.right, front_rect.bottom),             # أسفل أمام يمين
            (front_rect.right - depth, front_rect.bottom - depth),  # أسفل خلف يمين
            (front_rect.right - depth, front_rect.top - depth),     # أعلى خلف يمين
        ]
        pygame.draw.polygon(surf, settings.COLOR_PLAYER_SUIT_SIDE, side_polygon)
        pygame.draw.polygon(surf, settings.COLOR_PLAYER_OUTLINE, side_polygon, 2)

        # ظل بسيط في أسفل الجسم
        bottom_shadow = pygame.Surface((w, h), pygame.SRCALPHA)
        shadow_rect = pygame.Rect(
            body_x,
            front_rect.bottom - 4,
            body_width,
            6,
        )
        pygame.draw.rect(bottom_shadow, (0, 0, 0, 80), shadow_rect, border_radius=4)
        surf.blit(bottom_shadow, (0, 0))

        # حزام
        belt_h = 6
        belt_rect = pygame.Rect(
            body_x + 4,
            body_y + body_height // 2,
            body_width - 8,
            belt_h,
        )
        pygame.draw.rect(surf, settings.COLOR_PLAYER_OUTLINE, belt_rect, border_radius=3)

        # لمبة في منتصف الصدر
        chest_light = pygame.Rect(
            body_x + body_width // 2 - 4,
            body_y + 8,
            8,
            8,
        )
        pygame.draw.rect(surf, settings.COLOR_PLAYER_ACCENT, chest_light, border_radius=3)

        # حفظ بعض الإحداثيات لاستخدامها في الأرجل
        return front_rect

    def _draw_limbs_3d(self, surf, front_rect):
        """أذرع وأرجل متوافقة مع الجسم 3D-Style."""

        w, h = self.width, self.height

        # الأذرع
        arm_width = int(w * 0.22)
        arm_height = int(front_rect.height * 0.7)
        arm_y = front_rect.y + 6

        left_arm = pygame.Rect(
            front_rect.x - arm_width + 4,
            arm_y,
            arm_width,
            arm_height,
        )
        right_arm = pygame.Rect(
            front_rect.right - 4,
            arm_y,
            arm_width,
            arm_height,
        )

        for arm in (left_arm, right_arm):
            pygame.draw.rect(surf, settings.COLOR_PLAYER_SUIT_FRONT, arm, border_radius=8)
            pygame.draw.rect(surf, settings.COLOR_PLAYER_OUTLINE, arm, 2, border_radius=8)

        # أرجل
        leg_width = front_rect.width // 3
        leg_height = h - (front_rect.bottom) - 4
        leg_y = front_rect.bottom

        left_leg = pygame.Rect(
            front_rect.x + 3,
            leg_y,
            leg_width,
            leg_height,
        )
        right_leg = pygame.Rect(
            front_rect.right - leg_width - 3,
            leg_y,
            leg_width,
            leg_height,
        )

        for leg in (left_leg, right_leg):
            pygame.draw.rect(surf, settings.COLOR_PLAYER_SUIT_FRONT, leg, border_radius=4)
            pygame.draw.rect(surf, settings.COLOR_PLAYER_OUTLINE, leg, 2, border_radius=4)

        # أقدام أغمق
        foot_h = 6
        left_foot = pygame.Rect(left_leg.x, left_leg.bottom - foot_h, leg_width, foot_h)
        right_foot = pygame.Rect(right_leg.x, right_leg.bottom - foot_h, leg_width, foot_h)
        for foot in (left_foot, right_foot):
            pygame.draw.rect(surf, settings.COLOR_PLAYER_OUTLINE, foot, border_radius=4)

    def _draw_idle(self):
        """إعادة رسم الشخصية في وضع الوقوف 3D-Style."""
        self.image.fill((0, 0, 0, 0))

        # جسم 3D
        front_rect = self._draw_body_3d(self.image)
        # أطراف
        self._draw_limbs_3d(self.image, front_rect)
        # رأس
        self._draw_head(self.image)

    # ---------------- الحركة والتحديث ----------------
    def handle_input(self, keys):
        dx, dy = 0, 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.speed
            self.facing = "up"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.speed
            self.facing = "down"
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.speed
            self.facing = "left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed
            self.facing = "right"

        self.rect.x += dx
        self.rect.y += dy

        # حدود الشاشة
        self.rect.clamp_ip(pygame.Rect(0, 0, settings.WIDTH, settings.HEIGHT))

    def update(self, keys):
        self.handle_input(keys)
        # لاحقاً تقدر تضيف هنا تغييرات بسيطة في الرسم حسب facing للحركة
