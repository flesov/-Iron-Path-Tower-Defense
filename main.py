import arcade
import math
import random
from typing import List, Optional

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "☢️ ANOMALY DEFENSE ☢️"

GRID_SIZE = 60
PATH_COLOR = (60, 50, 70)
GRID_COLOR = (40, 60, 40)

PATH = [
    (0, 400), (300, 400), (300, 200), (600, 200),
    (600, 500), (900, 500), (900, 300), (1200, 300)
]

# Пиксельные цвета
PIXEL_COLORS = {
    'dark_green': (20, 50, 20),
    'green': (40, 80, 40),
    'light_green': (60, 120, 60),
    'red': (180, 40, 40),
    'dark_red': (120, 20, 20),
    'blue': (40, 80, 180),
    'cyan': (40, 180, 180),
    'yellow': (220, 200, 40),
    'orange': (220, 120, 40),
    'purple': (120, 40, 180),
    'pink': (220, 80, 160),
    'white': (240, 240, 240),
    'black': (20, 20, 30),
    'gray': (80, 80, 90),
}


class Particle:
    """Частица для эффектов"""

    def __init__(self, x, y, vx, vy, color, size=3, lifetime=30, gravity=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.alpha = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy -= self.gravity
        self.lifetime -= 1
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        self.size = max(1, self.size * 0.98)

    def draw(self):
        if self.lifetime > 0:
            color = (*self.color[:3], self.alpha)
            # Пиксельный стиль - квадраты вместо кругов
            draw_rectangle_filled(self.x, self.y, self.size, self.size, color)

def draw_rectangle_filled(x, y, width, height, color):
    """Обёртка для совместимости с Arcade 3.0+"""
    arcade.draw_rect_filled(
        arcade.XYWH(x, y, width, height),
        color
    )

def draw_rectangle_outline(x, y, width, height, color, border_width=1):
    """Обёртка для совместимости с Arcade 3.0+"""
    arcade.draw_rect_outline(
        arcade.XYWH(x, y, width, height),
        color,
        border_width
    )

class ParticleSystem:
    """Система частиц"""

    def __init__(self):
        self.particles: List[Particle] = []

    def add_particle(self, particle):
        self.particles.append(particle)

    def emit_explosion(self, x, y, color, count=10):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            self.add_particle(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                color,
                size=random.randint(2, 5),
                lifetime=random.randint(20, 40),
                gravity=0.1
            ))

    def emit_anomaly(self, x, y):
        """Эффект аномалии"""
        colors = [PIXEL_COLORS['purple'], PIXEL_COLORS['pink'], PIXEL_COLORS['cyan']]
        for _ in range(5):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(10, 30)
            self.add_particle(Particle(
                x + math.cos(angle) * dist,
                y + math.sin(angle) * dist,
                random.uniform(-0.5, 0.5),
                random.uniform(0.5, 2),
                random.choice(colors),
                size=random.randint(2, 4),
                lifetime=random.randint(30, 50)
            ))

    def emit_trail(self, x, y, color):
        """След от движения"""
        self.add_particle(Particle(
            x + random.uniform(-3, 3),
            y + random.uniform(-3, 3),
            0, 0, color,
            size=random.randint(2, 4),
            lifetime=15
        ))

    def emit_muzzle_flash(self, x, y, angle):
        """Вспышка выстрела"""
        colors = [PIXEL_COLORS['yellow'], PIXEL_COLORS['orange'], PIXEL_COLORS['white']]
        for i in range(8):
            spread = random.uniform(-0.3, 0.3)
            speed = random.uniform(3, 6)
            self.add_particle(Particle(
                x, y,
                math.cos(angle + spread) * speed,
                math.sin(angle + spread) * speed,
                random.choice(colors),
                size=random.randint(2, 4),
                lifetime=random.randint(8, 15)
            ))

    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def draw(self):
        for particle in self.particles:
            particle.draw()


class PixelArt:
    """Класс для рисования пиксельной графики"""

    @staticmethod
    def draw_pixel_rect(x, y, width, height, color, outline_color=None):
        """Пиксельный прямоугольник с обводкой"""
        draw_rectangle_filled(x, y, width, height, color)
        if outline_color:
            # Пиксельная обводка
            pixel = 2
            draw_rectangle_filled(x, y + height // 2, width, pixel, outline_color)
            draw_rectangle_filled(x, y - height // 2, width, pixel, outline_color)
            draw_rectangle_filled(x - width // 2, y, pixel, height, outline_color)
            draw_rectangle_filled(x + width // 2, y, pixel, height, outline_color)

    @staticmethod
    def draw_pixel_circle(x, y, radius, color, segments=8):
        """Пиксельный круг (октагон)"""
        points = []
        for i in range(segments):
            angle = (i / segments) * math.pi * 2
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            points.append((px, py))
        arcade.draw_polygon_filled(points, color)

    @staticmethod
    def draw_enemy_normal(x, y, size, health_percent, frame, hit_flash=0):
        """Обычный враг - пиксельный демон"""
        # Анимация
        breathe = math.sin(frame * 0.15) * 2
        bob = math.sin(frame * 0.2) * 1.5

        # Эффект покраснения при попадании
        flash_intensity = min(1.0, hit_flash / 10) if hit_flash > 0 else 0

        # Тень
        draw_rectangle_filled(x, y - size * 0.4, size * 0.8, 4, (20, 20, 20, 100))

        # Тело (градиент из слоёв) - с эффектом покраснения
        body_colors = [(100, 30, 30), (140, 40, 40), (180, 50, 50)]
        for i, color in enumerate(body_colors):
            layer_size = size - i * 4 + breathe
            # Применяем эффект покраснения
            if flash_intensity > 0:
                color = (
                    min(255, int(color[0] + (255 - color[0]) * flash_intensity)),
                    min(255, int(color[1] + (100 - color[1]) * flash_intensity)),
                    min(255, int(color[2] + (100 - color[2]) * flash_intensity))
                )
            draw_rectangle_filled(x, y + bob, layer_size, layer_size * 0.9, color)

        # Рога
        horn_color = (60, 20, 20)
        draw_rectangle_filled(x - size * 0.35, y + size * 0.4 + bob, 5, 12, horn_color)
        draw_rectangle_filled(x + size * 0.35, y + size * 0.4 + bob, 5, 12, horn_color)
        draw_rectangle_filled(x - size * 0.35, y + size * 0.55 + bob, 5, 5, horn_color)
        draw_rectangle_filled(x + size * 0.35, y + size * 0.55 + bob, 5, 5, horn_color)

        # Лицо - тёмная область
        draw_rectangle_filled(x, y + size * 0.1 + bob, size * 0.7, size * 0.4, (40, 15, 15))

        # Глаза (злые, светятся)
        eye_glow = abs(math.sin(frame * 0.1)) * 0.3 + 0.7
        eye_color = (int(255 * eye_glow), int(100 * eye_glow), 0)

        # Глаза моргают
        eye_open = (frame % 90) > 8
        if eye_open:
            # Белки
            draw_rectangle_filled(x - size * 0.18, y + size * 0.15 + bob, 8, 6, (255, 200, 150))
            draw_rectangle_filled(x + size * 0.18, y + size * 0.15 + bob, 8, 6, (255, 200, 150))
            # Зрачки
            draw_rectangle_filled(x - size * 0.18, y + size * 0.15 + bob, 4, 5, eye_color)
            draw_rectangle_filled(x + size * 0.18, y + size * 0.15 + bob, 4, 5, eye_color)
        else:
            # Закрытые глаза
            draw_rectangle_filled(x - size * 0.18, y + size * 0.15 + bob, 8, 2, (40, 15, 15))
            draw_rectangle_filled(x + size * 0.18, y + size * 0.15 + bob, 8, 2, (40, 15, 15))

        # Рот (зубастый)
        draw_rectangle_filled(x, y - size * 0.1 + bob, size * 0.4, 4, (20, 5, 5))
        # Зубы
        for i in range(3):
            tooth_x = x - 6 + i * 6
            draw_rectangle_filled(tooth_x, y - size * 0.1 + bob, 3, 5, (240, 230, 200))

        # Ножки с анимацией ходьбы
        leg_anim = math.sin(frame * 0.25) * 4
        draw_rectangle_filled(x - size * 0.25, y - size * 0.55 + leg_anim, 8, 10, (100, 30, 30))
        draw_rectangle_filled(x + size * 0.25, y - size * 0.55 - leg_anim, 8, 10, (100, 30, 30))
        # Ступни
        draw_rectangle_filled(x - size * 0.25, y - size * 0.65 + leg_anim, 10, 4, (60, 20, 20))
        draw_rectangle_filled(x + size * 0.25, y - size * 0.65 - leg_anim, 10, 4, (60, 20, 20))

    @staticmethod
    def draw_enemy_fast(x, y, size, health_percent, frame, hit_flash=0):
        """Быстрый враг - энергетический призрак"""
        # Мерцание
        flicker = 0.7 + math.sin(frame * 0.5) * 0.3
        alpha = int(200 * flicker)

        # Эффект покраснения при попадании
        flash_intensity = min(1.0, hit_flash / 10) if hit_flash > 0 else 0

        # Цвета с прозрачностью - с эффектом покраснения
        if flash_intensity > 0:
            body_color = (
                min(255, int(40 + (255 - 40) * flash_intensity)),
                min(255, int(180 + (100 - 180) * flash_intensity)),
                min(255, int(220 + (100 - 220) * flash_intensity)),
                alpha
            )
            core_color = (255, 150, 150, min(255, alpha + 50))
        else:
            body_color = (40, 180, 220, alpha)
            core_color = (100, 220, 255, min(255, alpha + 50))
        dark_color = (20, 80, 120, alpha)

        # Тень (размытая)
        draw_rectangle_filled(x + 3, y - 3, size * 0.6, size * 0.3, (20, 60, 80, 60))

        # Хвост энергии (волнистый)
        for i in range(4):
            tail_offset = math.sin(frame * 0.3 + i * 0.8) * 4
            tail_y = y - size * 0.3 - i * 6
            tail_alpha = alpha - i * 40
            if tail_alpha > 0:
                tail_width = size * 0.4 - i * 3
                draw_rectangle_filled(x + tail_offset, tail_y, tail_width, 5,
                                      (40, 150, 200, tail_alpha))

        # Основное тело (капля/призрак)
        # Нижняя часть
        draw_rectangle_filled(x, y - size * 0.15, size * 0.5, size * 0.4, body_color)
        # Верхняя часть (голова)
        draw_rectangle_filled(x, y + size * 0.2, size * 0.7, size * 0.5, body_color)
        # Округление
        draw_rectangle_filled(x, y + size * 0.45, size * 0.5, size * 0.2, body_color)

        # Ядро (светящееся)
        core_pulse = abs(math.sin(frame * 0.2)) * 3
        draw_rectangle_filled(x, y + size * 0.1, size * 0.35 + core_pulse,
                              size * 0.35 + core_pulse, core_color)

        # Глаза (большие, без зрачков - пустые)
        eye_y = y + size * 0.25
        # Внешний контур глаз
        draw_rectangle_filled(x - size * 0.18, eye_y, 10, 12, (0, 40, 60, alpha))
        draw_rectangle_filled(x + size * 0.18, eye_y, 10, 12, (0, 40, 60, alpha))
        # Свечение глаз
        eye_glow = abs(math.sin(frame * 0.15)) * 50 + 200
        draw_rectangle_filled(x - size * 0.18, eye_y, 6, 8, (eye_glow, 255, 255, alpha))
        draw_rectangle_filled(x + size * 0.18, eye_y, 6, 8, (eye_glow, 255, 255, alpha))

        # Энергетические искры вокруг
        for i in range(3):
            spark_angle = frame * 0.1 + i * 2.1
            spark_dist = size * 0.5 + math.sin(frame * 0.2 + i) * 5
            spark_x = x + math.cos(spark_angle) * spark_dist
            spark_y = y + math.sin(spark_angle) * spark_dist
            spark_alpha = int(150 + math.sin(frame * 0.3 + i) * 100)
            if spark_alpha > 0:
                draw_rectangle_filled(spark_x, spark_y, 3, 3, (150, 255, 255, spark_alpha))

    @staticmethod
    def draw_enemy_tank(x, y, size, health_percent, frame, hit_flash=0):
        """Танковый враг - бронированный голем"""
        # Анимация шага
        step = abs(math.sin(frame * 0.08)) * 3
        shake = math.sin(frame * 0.15) * 1

        # Эффект покраснения при попадании
        flash_intensity = min(1.0, hit_flash / 10) if hit_flash > 0 else 0

        # Тень
        draw_rectangle_filled(x + 4, y - size * 0.5, size * 0.9, 8, (20, 20, 20, 80))

        # Ноги (массивные)
        leg_color = (50, 50, 60)
        leg_anim = math.sin(frame * 0.1) * 2
        # Левая нога
        draw_rectangle_filled(x - size * 0.3, y - size * 0.55 - leg_anim, 14, 20, leg_color)
        draw_rectangle_filled(x - size * 0.3, y - size * 0.7 - leg_anim, 18, 8, (40, 40, 50))
        # Правая нога
        draw_rectangle_filled(x + size * 0.3, y - size * 0.55 + leg_anim, 14, 20, leg_color)
        draw_rectangle_filled(x + size * 0.3, y - size * 0.7 + leg_anim, 18, 8, (40, 40, 50))

        # Основное тело (многослойная броня) - с эффектом покраснения
        body_y = y + step

        def apply_flash(color):
            if flash_intensity > 0:
                return (
                    min(255, int(color[0] + (255 - color[0]) * flash_intensity)),
                    min(255, int(color[1] + (100 - color[1]) * flash_intensity)),
                    min(255, int(color[2] + (100 - color[2]) * flash_intensity))
                )
            return color

        # Нижняя броня
        draw_rectangle_filled(x + shake, body_y - size * 0.2, size * 1.1, size * 0.4, apply_flash((60, 60, 70)))

        # Центральная часть
        draw_rectangle_filled(x + shake, body_y, size * 1.0, size * 0.6, apply_flash((80, 80, 95)))

        # Верхняя броня
        draw_rectangle_filled(x + shake, body_y + size * 0.25, size * 0.9, size * 0.35, apply_flash((100, 100, 115)))

        # Броневые пластины (горизонтальные линии)
        plate_color = apply_flash((50, 50, 60))
        for i in range(4):
            plate_y = body_y - size * 0.3 + i * (size * 0.2)
            draw_rectangle_filled(x + shake, plate_y, size * 0.95, 3, plate_color)

        # Заклёпки
        rivet_color = apply_flash((120, 120, 130))
        for i in range(3):
            for j in range(2):
                rivet_x = x - size * 0.35 + j * size * 0.7 + shake
                rivet_y = body_y - size * 0.2 + i * size * 0.25
                draw_rectangle_filled(rivet_x, rivet_y, 4, 4, rivet_color)

        # Плечи
        draw_rectangle_filled(x - size * 0.5 + shake, body_y + size * 0.1, 12, 20, apply_flash((70, 70, 80)))
        draw_rectangle_filled(x + size * 0.5 + shake, body_y + size * 0.1, 12, 20, apply_flash((70, 70, 80)))

        # Голова/шлем
        head_y = body_y + size * 0.45
        draw_rectangle_filled(x + shake, head_y, size * 0.5, size * 0.3, apply_flash((90, 90, 100)))
        draw_rectangle_filled(x + shake, head_y + size * 0.1, size * 0.4, size * 0.15, apply_flash((70, 70, 80)))

        # Визор (красный глаз)
        visor_glow = abs(math.sin(frame * 0.12)) * 0.5 + 0.5
        visor_color = (int(200 * visor_glow), int(40 * visor_glow), int(40 * visor_glow))
        draw_rectangle_filled(x + shake, head_y, size * 0.4, 6, (20, 0, 0))
        draw_rectangle_filled(x + shake, head_y, size * 0.35, 4, visor_color)

        # Свечение визора
        if visor_glow > 0.7:
            draw_rectangle_filled(x + shake, head_y, size * 0.45, 8, (*visor_color, 50))

        # Индикатор здоровья на броне (встроенный)
        if health_percent < 1.0:
            # Трещины при низком здоровье
            if health_percent < 0.5:
                crack_color = (40, 40, 45)
                draw_rectangle_filled(x - size * 0.2 + shake, body_y + size * 0.1, 2, 15, crack_color)
                draw_rectangle_filled(x + size * 0.15 + shake, body_y - size * 0.1, 2, 20, crack_color)
            if health_percent < 0.25:
                # Искры от повреждений
                if frame % 10 < 5:
                    spark_x = x + random.randint(-int(size * 0.3), int(size * 0.3))
                    spark_y = body_y + random.randint(-int(size * 0.2), int(size * 0.2))
                    draw_rectangle_filled(spark_x, spark_y, 3, 3, (255, 200, 50))

    @staticmethod
    def draw_tower_basic(x, y, angle, level, frame):
        """Базовая турель"""
        base_color = PIXEL_COLORS['dark_green']
        gun_color = PIXEL_COLORS['green']
        accent_color = PIXEL_COLORS['light_green']

        # База (восьмиугольник)
        PixelArt.draw_pixel_circle(x, y, 18, base_color)
        PixelArt.draw_pixel_circle(x, y, 14, gun_color)

        # Пушка (вращается)
        gun_length = 20 + level * 3
        gun_width = 6 + level

        end_x = x + math.cos(angle) * gun_length
        end_y = y + math.sin(angle) * gun_length

        # Рисуем пушку как линию из квадратов
        steps = 5
        for i in range(steps):
            t = i / steps
            px = x + (end_x - x) * t
            py = y + (end_y - y) * t
            draw_rectangle_filled(px, py, gun_width, gun_width, gun_color)

        # Дуло
        draw_rectangle_filled(end_x, end_y, gun_width + 2, gun_width + 2, accent_color)

        # Индикатор уровня
        for i in range(level):
            draw_rectangle_filled(x - 10 + i * 8, y - 22, 6, 4, PIXEL_COLORS['yellow'])

    @staticmethod
    def draw_tower_sniper(x, y, angle, level, frame):
        """Снайперская турель"""
        base_color = PIXEL_COLORS['blue']
        gun_color = (60, 100, 200)
        accent_color = PIXEL_COLORS['cyan']

        # База
        draw_rectangle_filled(x, y, 30, 30, base_color)
        draw_rectangle_filled(x, y, 22, 22, gun_color)

        # Длинная пушка
        gun_length = 30 + level * 5
        gun_width = 4

        end_x = x + math.cos(angle) * gun_length
        end_y = y + math.sin(angle) * gun_length

        # Ствол
        for i in range(8):
            t = i / 8
            px = x + (end_x - x) * t
            py = y + (end_y - y) * t
            draw_rectangle_filled(px, py, gun_width, gun_width, gun_color)

        # Прицел
        scope_x = x + math.cos(angle) * 15
        scope_y = y + math.sin(angle) * 15
        draw_rectangle_filled(scope_x, scope_y + 6, 6, 8, accent_color)

        # Лазерный луч (мигает)
        if frame % 10 < 5:
            laser_end_x = x + math.cos(angle) * 100
            laser_end_y = y + math.sin(angle) * 100
            arcade.draw_line(end_x, end_y, laser_end_x, laser_end_y, (*accent_color, 100), 1)

    @staticmethod
    def draw_tower_slow(x, y, angle, level, frame):
        """Замедляющая турель"""
        # Анимация пульсации
        pulse = abs(math.sin(frame * 0.1)) * 5

        base_color = PIXEL_COLORS['purple']
        core_color = PIXEL_COLORS['pink']

        # Кристаллическая форма
        points = []
        for i in range(6):
            a = (i / 6) * math.pi * 2 + frame * 0.02
            r = 16 + (i % 2) * 5 + pulse
            points.append((x + math.cos(a) * r, y + math.sin(a) * r))
        arcade.draw_polygon_filled(points, base_color)

        # Ядро
        PixelArt.draw_pixel_circle(x, y, 8 + pulse * 0.3, core_color)

        # Энергетические кольца
        for i in range(3):
            ring_r = 25 + i * 10 + pulse
            alpha = int(100 - i * 30)
            arcade.draw_circle_outline(x, y, ring_r, (*PIXEL_COLORS['cyan'], alpha), 2)


class Bullet(arcade.Sprite):
    def __init__(self, x, y, target, damage, speed=8, bullet_type="normal"):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.target = target
        self.damage = damage
        self.speed = speed
        self.bullet_type = bullet_type
        self.trail_timer = 0
        self.angle = 0

        if bullet_type == "sniper":
            self.color = PIXEL_COLORS['cyan']
            self.bullet_size = 6  # БЫЛО: self.size = 6
        elif bullet_type == "slow":
            self.color = PIXEL_COLORS['purple']
            self.bullet_size = 8  # БЫЛО: self.size = 8
        else:
            self.color = PIXEL_COLORS['yellow']
            self.bullet_size = 5  # БЫЛО: self.size = 5

    def update(self, delta_time=0, particles=None):
        if not self.target or self.target.health <= 0:
            self.remove_from_sprite_lists()
            return False

        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        self.angle = math.atan2(dy, dx)

        if distance < 15:
            self.target.health -= self.damage
            self.target.hit_flash_timer = 10  # Включаем эффект покраснения на 10 кадров
            # Воспроизведение звука при попадании
            try:
                sound = arcade.load_sound("hit.wav")
                arcade.play_sound(sound)
            except Exception:
                pass
            if particles:
                particles.emit_explosion(self.center_x, self.center_y, self.color, 5)
            self.remove_from_sprite_lists()
            return True

        self.center_x += (dx / distance) * self.speed
        self.center_y += (dy / distance) * self.speed

        # След
        self.trail_timer += 1
        if self.trail_timer % 2 == 0 and particles:
            particles.emit_trail(self.center_x, self.center_y, self.color)

        return False

    def draw(self):
        # Пиксельная пуля
        draw_rectangle_filled(
            self.center_x, self.center_y,
            self.bullet_size, self.bullet_size, self.color  # БЫЛО: self.size
        )
        # Свечение
        draw_rectangle_filled(
            self.center_x, self.center_y,
            self.bullet_size + 2, self.bullet_size + 2, (*self.color[:3], 100)  # БЫЛО: self.size
        )


class Enemy(arcade.Sprite):
    def __init__(self, path, enemy_type="normal"):
        super().__init__()
        self.path = path
        self.path_index = 0
        self.center_x = path[0][0]
        self.center_y = path[0][1]
        self.frame = random.randint(0, 100)
        self.dead = False
        self.death_timer = 0

        self.enemy_type = enemy_type
        if enemy_type == "fast":
            self.max_health = 120
            self.speed = 2.8
            self.reward = 15
            self.enemy_size = 20  # БЫЛО: self.size = 20
        elif enemy_type == "tank":
            self.max_health = 600
            self.speed = 0.7
            self.reward = 60
            self.enemy_size = 35  # БЫЛО: self.size = 35
        else:
            self.max_health = 180
            self.speed = 1.5
            self.reward = 25
            self.enemy_size = 25  # БЫЛО: self.size = 25

        self.health = self.max_health
        self.slow_factor = 1.0
        self.width = self.enemy_size   # БЫЛО: self.size
        self.height = self.enemy_size  # БЫЛО: self.size
        self.hit_flash_timer = 0  # Таймер для эффекта покраснения при попадании

    def update(self, delta_time=0, particles=None):
        self.frame += 1

        if self.dead:
            self.death_timer += 1
            return

        if self.path_index >= len(self.path) - 1:
            return

        target_x, target_y = self.path[self.path_index + 1]
        dx = target_x - self.center_x
        dy = target_y - self.center_y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < 5:
            self.path_index += 1
        else:
            move_speed = self.speed * self.slow_factor
            self.center_x += (dx / distance) * move_speed
            self.center_y += (dy / distance) * move_speed

            # След при замедлении
            if self.slow_factor < 1.0 and particles and self.frame % 5 == 0:
                particles.emit_trail(self.center_x, self.center_y, PIXEL_COLORS['cyan'])

        self.slow_factor = min(1.0, self.slow_factor + 0.02)

        # Уменьшаем таймер покраснения
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1

    def draw(self):
        if self.dead:
            return

        health_percent = self.health / self.max_health

        # Отрисовка врага
        if self.enemy_type == "fast":
            PixelArt.draw_enemy_fast(self.center_x, self.center_y, self.enemy_size, health_percent, self.frame, self.hit_flash_timer)
        elif self.enemy_type == "tank":
            PixelArt.draw_enemy_tank(self.center_x, self.center_y, self.enemy_size, health_percent, self.frame, self.hit_flash_timer)
        else:
            PixelArt.draw_enemy_normal(self.center_x, self.center_y, self.enemy_size, health_percent, self.frame, self.hit_flash_timer)

        # Полоска здоровья
        bar_width = self.enemy_size  # БЫЛО: self.size
        bar_height = 4
        bar_y = self.center_y + self.enemy_size / 2 + 10  # БЫЛО: self.size

        # Фон
        draw_rectangle_filled(
            self.center_x, bar_y, bar_width + 2, bar_height + 2, PIXEL_COLORS['black']
        )
        # Здоровье
        health_width = bar_width * health_percent
        health_color = PIXEL_COLORS['green'] if health_percent > 0.5 else (
            PIXEL_COLORS['yellow'] if health_percent > 0.25 else PIXEL_COLORS['red']
        )
        draw_rectangle_filled(
            self.center_x - (bar_width - health_width) / 2,
            bar_y, health_width, bar_height, health_color
        )

class Tower(arcade.Sprite):
    def __init__(self, x, y, tower_type="basic"):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.tower_type = tower_type
        self.level = 1
        self.angle = 0
        self.frame = 0

        if tower_type == "sniper":
            self.range = 250
            self.damage = 80
            self.fire_rate = 90
            self.cost = 200
            self.upgrade_cost = 150
        elif tower_type == "slow":
            self.range = 150
            self.damage = 10
            self.fire_rate = 30
            self.cost = 150
            self.upgrade_cost = 100
            self.slow_effect = 0.4
        else:
            self.range = 180
            self.damage = 40
            self.fire_rate = 45
            self.cost = 100
            self.upgrade_cost = 80

        self.width = 40
        self.height = 40
        self.fire_cooldown = 0
        self.target = None

    def update(self, enemies, delta_time=0):
        self.frame += 1
        self.fire_cooldown = max(0, self.fire_cooldown - 1)

        if self.target and (self.target.health <= 0 or
                            self.get_distance(self.target) > self.range):
            self.target = None

        if not self.target:
            for enemy in enemies:
                if self.get_distance(enemy) <= self.range:
                    self.target = enemy
                    break

        # Плавный поворот к цели
        if self.target:
            target_angle = math.atan2(
                self.target.center_y - self.center_y,
                self.target.center_x - self.center_x
            )
            angle_diff = target_angle - self.angle
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            self.angle += angle_diff * 0.15

    def get_distance(self, enemy):
        return math.sqrt((self.center_x - enemy.center_x) ** 2 +
                         (self.center_y - enemy.center_y) ** 2)

    def can_fire(self):
        return self.fire_cooldown == 0 and self.target and self.target.health > 0

    def fire(self, particles=None):
        self.fire_cooldown = self.fire_rate

        # Эффект выстрела
        if particles:
            muzzle_x = self.center_x + math.cos(self.angle) * 20
            muzzle_y = self.center_y + math.sin(self.angle) * 20
            particles.emit_muzzle_flash(muzzle_x, muzzle_y, self.angle)

        if self.tower_type == "slow" and self.target:
            self.target.slow_factor = self.slow_effect

        bullet_type = self.tower_type if self.tower_type in ["sniper", "slow"] else "normal"
        return Bullet(self.center_x, self.center_y, self.target, self.damage,
                      speed=12 if self.tower_type == "sniper" else 8, bullet_type=bullet_type)

    def upgrade(self):
        self.level += 1
        self.damage = int(self.damage * 1.2)  # было 1.5
        self.range = int(self.range * 1.05)  # было 1.1
        self.fire_rate = int(self.fire_rate * 0.93)  # было 0.85
        self.upgrade_cost = int(self.upgrade_cost * 1.6)

    def draw(self, selected=False):
        if self.tower_type == "basic":
            PixelArt.draw_tower_basic(self.center_x, self.center_y, self.angle, self.level, self.frame)
        elif self.tower_type == "sniper":
            PixelArt.draw_tower_sniper(self.center_x, self.center_y, self.angle, self.level, self.frame)
        else:
            PixelArt.draw_tower_slow(self.center_x, self.center_y, self.angle, self.level, self.frame)

        if selected:
            # Пиксельная обводка выбора
            draw_rectangle_outline(self.center_x, self.center_y, 50, 50,
                                          PIXEL_COLORS['yellow'], 2)


class WaveManager:
    def __init__(self):
        self.wave = 0
        self.active = False
        self.spawn_timer = 0
        self.spawn_interval = 50
        self.enemies_to_spawn = []
        self.wave_text_timer = 0

    def start_wave(self):
        self.wave += 1
        self.active = True
        self.spawn_timer = 0
        self.wave_text_timer = 120

        # Воспроизведение звука при старте новой волны
        try:
            sound = arcade.load_sound("lvl_up.wav")
            arcade.play_sound(sound)
        except Exception:
            pass

        enemy_count = 5 + self.wave * 3
        self.enemies_to_spawn = []

        for i in range(enemy_count):
            if self.wave >= 5 and random.random() < 0.2:
                self.enemies_to_spawn.append("tank")
            elif random.random() < 0.3:
                self.enemies_to_spawn.append("fast")
            else:
                self.enemies_to_spawn.append("normal")

    def update(self):
        self.wave_text_timer = max(0, self.wave_text_timer - 1)

        if not self.active or not self.enemies_to_spawn:
            return None

        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            enemy_type = self.enemies_to_spawn.pop(0)
            if not self.enemies_to_spawn:
                self.active = False
            return Enemy(PATH, enemy_type)
        return None


class MainMenu:
    """Главное меню"""

    def __init__(self):
        self.frame = 0
        self.particles = ParticleSystem()
        self.selected_option = 0
        self.options = ["НАЧАТЬ ИГРУ", "УПРАВЛЕНИЕ", "ВЫХОД"]
        self.show_controls = False

    def update(self):
        self.frame += 1
        self.particles.update()

        # Генерация фоновых частиц
        if self.frame % 10 == 0:
            x = random.randint(0, SCREEN_WIDTH)
            self.particles.emit_anomaly(x, random.randint(100, 700))

    def draw(self):
        # Фон с градиентом
        for y in range(0, SCREEN_HEIGHT, 4):
            color_val = int(20 + (y / SCREEN_HEIGHT) * 30)
            draw_rectangle_filled(
                SCREEN_WIDTH // 2, y, SCREEN_WIDTH, 4,
                (color_val, color_val + 10, color_val)
            )

        # Сетка на фоне
        for x in range(0, SCREEN_WIDTH, 40):
            alpha = int(50 + math.sin(self.frame * 0.02 + x * 0.01) * 20)
            arcade.draw_line(x, 0, x, SCREEN_HEIGHT, (40, 60, 40, alpha), 1)
        for y in range(0, SCREEN_HEIGHT, 40):
            alpha = int(50 + math.sin(self.frame * 0.02 + y * 0.01) * 20)
            arcade.draw_line(0, y, SCREEN_WIDTH, y, (40, 60, 40, alpha), 1)

        self.particles.draw()

        # Заголовок с эффектом глитча
        title = "☢️ ANOMALY DEFENSE ☢️"
        glitch_offset = random.randint(-2, 2) if random.random() < 0.1 else 0

        # Тень заголовка
        arcade.draw_text(title, SCREEN_WIDTH // 2 + 4 + glitch_offset,
                         SCREEN_HEIGHT - 150 - 4, PIXEL_COLORS['black'],
                         48, anchor_x="center", bold=True)

        # Основной заголовок
        arcade.draw_text(title, SCREEN_WIDTH // 2 + glitch_offset,
                         SCREEN_HEIGHT - 150, PIXEL_COLORS['green'],
                         48, anchor_x="center", bold=True)

        # Подзаголовок
        subtitle = "TOWER DEFENSE"
        arcade.draw_text(subtitle, SCREEN_WIDTH // 2,
                         SCREEN_HEIGHT - 200, PIXEL_COLORS['cyan'],
                         24, anchor_x="center")

        if self.show_controls:
            self.draw_controls()
        else:
            # Пункты меню
            for i, option in enumerate(self.options):
                y = SCREEN_HEIGHT // 2 - i * 60

                if i == self.selected_option:
                    # Выбранный пункт
                    pulse = abs(math.sin(self.frame * 0.1)) * 10
                    draw_rectangle_filled(SCREEN_WIDTH // 2, y, 300 + pulse, 50,
                                                 (*PIXEL_COLORS['green'], 50))
                    draw_rectangle_outline(SCREEN_WIDTH // 2, y, 300, 50,
                                                  PIXEL_COLORS['green'], 3)
                    color = PIXEL_COLORS['white']
                    prefix = "> "
                else:
                    color = PIXEL_COLORS['gray']
                    prefix = "  "

                arcade.draw_text(prefix + option, SCREEN_WIDTH // 2, y,
                                 color, 24, anchor_x="center", anchor_y="center", bold=True)

        # Подсказка
        hint_alpha = int(abs(math.sin(self.frame * 0.05)) * 200) + 55
        arcade.draw_text("↑↓ - ВЫБОР   ENTER - ПОДТВЕРДИТЬ",
                         SCREEN_WIDTH // 2, 50, (*PIXEL_COLORS['gray'], hint_alpha),
                         16, anchor_x="center")

    def draw_controls(self):
        # Панель управления
        draw_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                     600, 400, (*PIXEL_COLORS['black'], 240))
        draw_rectangle_outline(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                      600, 400, PIXEL_COLORS['green'], 3)

        controls = [
            "УПРАВЛЕНИЕ:",
            "",
            "ЛКМ - Установить турель / Выбрать",
            "1, 2, 3 - Выбор типа турели",
            "ESC - Пауза",
            "ЛКМ x2 на турель - Улучшение",
            "",
            "ТИПЫ ТУРЕЛЕЙ:",
            "BASIC - Сбалансированная ($100)",
            "SNIPER - Дальнобойная ($200)",
            "SLOW - Замедляющая ($150)",
            "",
            "[ENTER - НАЗАД]"
        ]

        for i, line in enumerate(controls):
            y = SCREEN_HEIGHT // 2 + 170 - i * 28
            color = PIXEL_COLORS['green'] if i == 0 or "ТУРЕЛЕЙ" in line else PIXEL_COLORS['white']
            arcade.draw_text(line, SCREEN_WIDTH // 2, y, color, 18,
                             anchor_x="center", bold=(i == 0 or "ТУРЕЛЕЙ" in line))


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color((20, 30, 20))

        self.state = "menu"  # menu, game, game_over
        self.main_menu = MainMenu()

        self.reset_game()

    def reset_game(self):
        self.towers = []
        self.enemies = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.particles = ParticleSystem()

        self.money = 300
        self.base_health = 3
        self.selected_tower_type = "basic"
        self.selected_tower = None

        self.wave_manager = WaveManager()
        self.game_over = False
        self.paused = False
        self.frame = 0
        self.screen_shake = 0

        self.mouse_x = 0
        self.mouse_y = 0

    def on_draw(self):
        self.clear()

        if self.state == "menu":
            self.main_menu.draw()
            return

        # Экран тряски
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0

        arcade.get_window().ctx.viewport = (shake_x, shake_y, SCREEN_WIDTH, SCREEN_HEIGHT)


        # Фон с сеткой - в методе on_draw
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            for y in range(0, SCREEN_HEIGHT - 100, GRID_SIZE):
                # Быстрая анимация (0.08)
                wave = math.sin(self.frame * 0.08 + x * 0.02 + y * 0.02) * 5
                base_color = (32 + int(wave), 52 + int(wave), 32)
                draw_rectangle_filled(x + GRID_SIZE // 2, y + GRID_SIZE // 2,
                                      GRID_SIZE - 2, GRID_SIZE - 2, base_color)

        # Путь с красивыми поворотами
        for i in range(len(PATH) - 1):
            # Основной путь
            arcade.draw_line(PATH[i][0], PATH[i][1], PATH[i + 1][0], PATH[i + 1][1],
                             (60, 50, 70), 44)
            # Разметка
            arcade.draw_line(PATH[i][0], PATH[i][1], PATH[i + 1][0], PATH[i + 1][1],
                             (80, 70, 90), 38)
            # Центральная линия (пунктир)
            length = math.sqrt((PATH[i + 1][0] - PATH[i][0]) ** 2 + (PATH[i + 1][1] - PATH[i][1]) ** 2)
            steps = int(length / 20)
            for j in range(0, steps, 2):
                t1 = j / steps
                t2 = min(1, (j + 1) / steps)
                x1 = PATH[i][0] + (PATH[i + 1][0] - PATH[i][0]) * t1
                y1 = PATH[i][1] + (PATH[i + 1][1] - PATH[i][1]) * t1
                x2 = PATH[i][0] + (PATH[i + 1][0] - PATH[i][0]) * t2
                y2 = PATH[i][1] + (PATH[i + 1][1] - PATH[i][1]) * t2
                arcade.draw_line(x1, y1, x2, y2, (100, 90, 110), 2)

        # Закругления на поворотах
        for i in range(1, len(PATH) - 1):
            px, py = PATH[i]

            # Многослойный круг для плавного перехода
            arcade.draw_circle_filled(px, py, 24, (50, 40, 60))  # Тень
            arcade.draw_circle_filled(px, py, 22, (60, 50, 70))  # Основа
            arcade.draw_circle_filled(px, py, 19, (80, 70, 90))  # Разметка

            # Декоративные элементы поворота
            arcade.draw_circle_outline(px, py, 15, (100, 90, 110), 2)
            arcade.draw_circle_filled(px, py, 4, (100, 90, 110))

            # Угловые метки (показывают направление)
            prev_x, prev_y = PATH[i - 1]
            next_x, next_y = PATH[i + 1]

            # Стрелки направления
            angle_in = math.atan2(py - prev_y, px - prev_x)
            angle_out = math.atan2(next_y - py, next_x - px)

            # Маленькие указатели
            for angle in [angle_in, angle_out]:
                marker_x = px + math.cos(angle) * 12
                marker_y = py + math.sin(angle) * 12
                arcade.draw_circle_filled(marker_x, marker_y, 3, (120, 110, 130))

        # Подсветка доступных ячеек
        grid_x = (self.mouse_x // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
        grid_y = (self.mouse_y // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2

        if (self.mouse_y < SCREEN_HEIGHT - 100 and
                self.is_valid_tower_position(grid_x, grid_y)):
            # Анимированная подсветка
            pulse = abs(math.sin(self.frame * 0.1)) * 30 + 50
            draw_rectangle_filled(grid_x, grid_y, GRID_SIZE - 4, GRID_SIZE - 4,
                                         (80, 150, 80, int(pulse)))
            draw_rectangle_outline(grid_x, grid_y, GRID_SIZE - 4, GRID_SIZE - 4,
                                          PIXEL_COLORS['green'], 2)

        # Частицы (под объектами)
        self.particles.draw()

        # Турели
        for tower in self.towers:
            tower.draw(selected=(tower == self.selected_tower))
            if tower == self.selected_tower:
                # Радиус действия
                arcade.draw_circle_outline(tower.center_x, tower.center_y,
                                           tower.range, (*PIXEL_COLORS['white'], 80), 2)

        # Враги
        for enemy in self.enemies:
            enemy.draw()

        # Пули
        for bullet in self.bullets:
            bullet.draw()

        # UI панель
        self.draw_ui()

        # Текст волны
        if self.wave_manager.wave_text_timer > 0:
            alpha = min(255, self.wave_manager.wave_text_timer * 4)
            scale = 1 + (120 - self.wave_manager.wave_text_timer) * 0.01
            arcade.draw_text(f"ВОЛНА {self.wave_manager.wave}",
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                             (*PIXEL_COLORS['red'], alpha),
                             int(48 * scale), anchor_x="center", bold=True)

        if self.game_over:
            self.draw_game_over()

        if self.paused and not self.game_over:
            self.draw_paused()

        # Сброс viewport
        arcade.get_window().ctx.viewport = (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

    def draw_ui(self):
        # Фон UI
        draw_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50,
                              SCREEN_WIDTH, 100, (30, 30, 40))
        arcade.draw_line(0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, SCREEN_HEIGHT - 100,
                         PIXEL_COLORS['green'], 3)

        # Деньги
        arcade.draw_text(f"${self.money}", 30, SCREEN_HEIGHT - 55,
                         PIXEL_COLORS['yellow'], 22, bold=True)

        # Здоровье базы
        health_color = PIXEL_COLORS['green'] if self.base_health > 10 else (
            PIXEL_COLORS['yellow'] if self.base_health > 5 else PIXEL_COLORS['red']
        )
        arcade.draw_text(f"HP: {self.base_health}", 150, SCREEN_HEIGHT - 55,
                         health_color, 22, bold=True)

        # Волна
        arcade.draw_text(f"WAVE {self.wave_manager.wave}", 280, SCREEN_HEIGHT - 55,
                         PIXEL_COLORS['cyan'], 22, bold=True)

        # Выбор турелей
        tower_types = [
            ("1:BASIC", "basic", 100, 450),
            ("2:SNIPER", "sniper", 200, 600),
            ("3:SLOW", "slow", 150, 750)
        ]

        for label, ttype, cost, btn_x in tower_types:
            is_selected = self.selected_tower_type == ttype
            can_afford = self.money >= cost

            # Проверка наведения мыши
            is_hovered = (btn_x - 65 <= self.mouse_x <= btn_x + 65 and
                          SCREEN_HEIGHT - 80 <= self.mouse_y <= SCREEN_HEIGHT - 20)

            # Фон кнопки
            if is_selected:
                bg_color = (60, 120, 60, 220)
            elif is_hovered:
                bg_color = (70, 70, 90, 200)
            else:
                bg_color = (50, 50, 60, 150)
            draw_rectangle_filled(btn_x, SCREEN_HEIGHT - 50, 130, 60, bg_color)

            # Рамка
            if is_selected:
                border_color = PIXEL_COLORS['green']
                border_width = 3
            elif is_hovered:
                border_color = PIXEL_COLORS['white']
                border_width = 2
            else:
                border_color = PIXEL_COLORS['gray']
                border_width = 1
            draw_rectangle_outline(btn_x, SCREEN_HEIGHT - 50, 130, 60, border_color, border_width)

            # Текст
            text_color = PIXEL_COLORS['white'] if can_afford else PIXEL_COLORS['red']
            arcade.draw_text(label, btn_x, SCREEN_HEIGHT - 40, text_color, 14,
                             anchor_x="center", bold=is_selected)
            arcade.draw_text(f"${cost}", btn_x, SCREEN_HEIGHT - 60, text_color, 12,
                             anchor_x="center")

        # Кнопка старта волны
        if not self.wave_manager.active and not self.enemies:
            start_hovered = (SCREEN_WIDTH - 175 <= self.mouse_x <= SCREEN_WIDTH - 25 and
                             SCREEN_HEIGHT - 78 <= self.mouse_y <= SCREEN_HEIGHT - 22)

            pulse = abs(math.sin(self.frame * 0.1)) * 10
            btn_color = PIXEL_COLORS['light_green'] if start_hovered else PIXEL_COLORS['green']
            draw_rectangle_filled(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 50,
                                  150 + pulse, 55, btn_color)
            draw_rectangle_outline(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 50,
                                   150, 55, PIXEL_COLORS['white'], 3)
            arcade.draw_text("START", SCREEN_WIDTH - 100, SCREEN_HEIGHT - 55,
                             PIXEL_COLORS['white'], 20, anchor_x="center", bold=True)

        # Информация о выбранной турели
        if self.selected_tower:
            info_text = f"LVL {self.selected_tower.level} | DMG: {self.selected_tower.damage} | UPGRADE: ${self.selected_tower.upgrade_cost}"
            arcade.draw_text(info_text, 450, SCREEN_HEIGHT - 90,
                             PIXEL_COLORS['yellow'], 12, bold=True)

    def draw_game_over(self):
        # Затемнение
        draw_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                     SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 200))

        # Рамка
        draw_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                     400, 250, PIXEL_COLORS['dark_red'])
        draw_rectangle_outline(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                      400, 250, PIXEL_COLORS['red'], 4)

        glitch = random.randint(-3, 3) if random.random() < 0.2 else 0
        arcade.draw_text("GAME OVER", SCREEN_WIDTH // 2 + glitch, SCREEN_HEIGHT // 2 + 50,
                         PIXEL_COLORS['red'], 40, anchor_x="center", bold=True)
        arcade.draw_text(f"Волна: {self.wave_manager.wave}", SCREEN_WIDTH // 2,
                         SCREEN_HEIGHT // 2, PIXEL_COLORS['white'], 24, anchor_x="center")
        arcade.draw_text("ENTER - В МЕНЮ", SCREEN_WIDTH // 2,
                         SCREEN_HEIGHT // 2 - 60, PIXEL_COLORS['gray'], 18, anchor_x="center")

    def draw_paused(self):
        draw_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                     300, 100, (0, 0, 0, 200))
        draw_rectangle_outline(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                      300, 100, PIXEL_COLORS['cyan'], 3)
        arcade.draw_text("⏸ ПАУЗА", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                         PIXEL_COLORS['white'], 32, anchor_x="center", anchor_y="center", bold=True)

    def on_update(self, delta_time):
        if self.state == "menu":
            self.main_menu.update()
            return

        if self.game_over or self.paused:
            return

        self.frame += 1
        self.screen_shake = max(0, self.screen_shake - 1)

        self.particles.update()

        # Аномальные эффекты на карте
        if self.frame % 60 == 0 and random.random() < 0.3:
            self.particles.emit_anomaly(
                random.randint(100, SCREEN_WIDTH - 100),
                random.randint(100, SCREEN_HEIGHT - 200)
            )

        new_enemy = self.wave_manager.update()
        if new_enemy:
            self.enemies.append(new_enemy)

        for enemy in self.enemies:
            enemy.update(delta_time, self.particles)

        for enemy in list(self.enemies):
            if enemy.health <= 0:
                self.money += enemy.reward
                self.particles.emit_explosion(enemy.center_x, enemy.center_y,
                                              PIXEL_COLORS['red'], 15)
                # Воспроизведение звука при смерти врага
                try:
                    sound = arcade.load_sound("death.wav")
                    arcade.play_sound(sound)
                except Exception:
                    pass
                self.enemies.remove(enemy)
            elif enemy.path_index >= len(PATH) - 1:
                self.base_health -= 1
                self.screen_shake = 10
                self.particles.emit_explosion(enemy.center_x, enemy.center_y,
                                              PIXEL_COLORS['orange'], 20)
                self.enemies.remove(enemy)
                if self.base_health <= 0:
                    self.game_over = True
                    self.screen_shake = 20

        for tower in self.towers:
            tower.update(self.enemies, delta_time)
            if tower.can_fire():
                self.bullets.append(tower.fire(self.particles))

        for bullet in list(self.bullets):
            hit = bullet.update(delta_time, self.particles)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        if self.state == "menu":
            if self.main_menu.show_controls:
                self.main_menu.show_controls = False
            return

        if self.game_over:
            return

        # Клик по UI панели
        if y > SCREEN_HEIGHT - 100:
            # Кнопки турелей - точные координаты как в draw_ui
            # Центры: 450, 600, 750. Ширина: 130
            tower_buttons = [
                ("basic", 450),
                ("sniper", 600),
                ("slow", 750)
            ]

            for tower_type, center_x in tower_buttons:
                # Проверяем попадание в кнопку (ширина 130, высота 60)
                if (center_x - 65 <= x <= center_x + 65 and
                        SCREEN_HEIGHT - 80 <= y <= SCREEN_HEIGHT - 20):
                    self.selected_tower_type = tower_type
                    return

            # Кнопка START
            if (SCREEN_WIDTH - 175 <= x <= SCREEN_WIDTH - 25 and
                    SCREEN_HEIGHT - 78 <= y <= SCREEN_HEIGHT - 22):
                if not self.wave_manager.active and not self.enemies:
                    self.wave_manager.start_wave()
            return

        # Клик по турели
        for tower in self.towers:
            dx = x - tower.center_x
            dy = y - tower.center_y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < 35:
                if self.selected_tower == tower:
                    if self.money >= tower.upgrade_cost:
                        self.money -= tower.upgrade_cost
                        tower.upgrade()
                        self.particles.emit_explosion(tower.center_x, tower.center_y,
                                                      PIXEL_COLORS['yellow'], 10)
                else:
                    self.selected_tower = tower
                return

        self.selected_tower = None

        # Установка турели
        grid_x = (x // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
        grid_y = (y // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2

        if not self.is_valid_tower_position(grid_x, grid_y):
            return

        tower_costs = {"basic": 100, "sniper": 200, "slow": 150}
        cost = tower_costs[self.selected_tower_type]

        if self.money >= cost:
            tower = Tower(grid_x, grid_y, self.selected_tower_type)
            self.towers.append(tower)
            self.money -= cost
            self.particles.emit_explosion(grid_x, grid_y, PIXEL_COLORS['green'], 8)

    def is_valid_tower_position(self, x, y):
        for i in range(len(PATH) - 1):
            # Проверка расстояния до сегмента пути
            x1, y1 = PATH[i]
            x2, y2 = PATH[i + 1]

            # Простая проверка
            for t in [0, 0.25, 0.5, 0.75, 1.0]:
                px = x1 + (x2 - x1) * t
                py = y1 + (y2 - y1) * t
                if abs(x - px) < 50 and abs(y - py) < 50:
                    return False

        for tower in self.towers:
            if abs(tower.center_x - x) < GRID_SIZE and abs(tower.center_y - y) < GRID_SIZE:
                return False
        return True

    def on_key_press(self, key, modifiers):
        if self.state == "menu":
            if self.main_menu.show_controls:
                if key == arcade.key.ENTER:
                    self.main_menu.show_controls = False
                return

            if key == arcade.key.UP:
                self.main_menu.selected_option = (self.main_menu.selected_option - 1) % 3
            elif key == arcade.key.DOWN:
                self.main_menu.selected_option = (self.main_menu.selected_option + 1) % 3
            elif key == arcade.key.ENTER:
                if self.main_menu.selected_option == 0:
                    self.state = "game"
                    self.reset_game()
                elif self.main_menu.selected_option == 1:
                    self.main_menu.show_controls = True
                elif self.main_menu.selected_option == 2:
                    arcade.close_window()
            return

        if self.game_over:
            if key == arcade.key.ENTER:
                self.state = "menu"
                self.main_menu = MainMenu()
            return

        if key == arcade.key.ESCAPE:
            self.paused = not self.paused
        elif key == arcade.key.KEY_1:
            self.selected_tower_type = "basic"
        elif key == arcade.key.KEY_2:
            self.selected_tower_type = "sniper"
        elif key == arcade.key.KEY_3:
            self.selected_tower_type = "slow"


def main():
    window = GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()