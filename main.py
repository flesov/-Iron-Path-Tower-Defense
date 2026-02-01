import arcade
import math
import random
from typing import List, Optional

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "🛡 Iron Path: Tower Defense"

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
    'gold': (255, 215, 0),
    'brown': (80, 50, 30),
    'dark_blue': (20, 40, 100),
    'dark_purple': (60, 20, 80),
    'metal': (120, 130, 140),
    'dark_metal': (60, 65, 70),
}


class Particle:

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
            draw_rectangle_filled(self.x, self.y, self.size, self.size, color)


def draw_rectangle_filled(x, y, width, height, color):
    arcade.draw_rect_filled(
        arcade.XYWH(x, y, width, height),
        color
    )


def draw_rectangle_outline(x, y, width, height, color, border_width=1):
    arcade.draw_rect_outline(
        arcade.XYWH(x, y, width, height),
        color,
        border_width
    )


class ParticleSystem:

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
        self.add_particle(Particle(
            x + random.uniform(-3, 3),
            y + random.uniform(-3, 3),
            0, 0, color,
            size=random.randint(2, 4),
            lifetime=15
        ))

    def emit_muzzle_flash(self, x, y, angle):
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

    def emit_ui_sparkle(self, x, y, color):
        for _ in range(3):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2)
            self.add_particle(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                color,
                size=random.randint(2, 4),
                lifetime=random.randint(15, 25)
            ))

    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def draw(self):
        for particle in self.particles:
            particle.draw()


class TowerCard:

    def __init__(self, x, y, tower_type, key, cost):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.key = key
        self.cost = cost
        self.width = 140
        self.height = 90

        self.hover_progress = 0.0
        self.select_progress = 0.0
        self.is_hovered = False
        self.is_selected = False
        self.frame = random.randint(0, 100)

        self.colors = {
            'basic': {
                'primary': (40, 120, 40),
                'secondary': (60, 180, 60),
                'glow': (100, 255, 100),
                'icon': PIXEL_COLORS['green']
            },
            'sniper': {
                'primary': (40, 80, 160),
                'secondary': (60, 120, 220),
                'glow': (100, 180, 255),
                'icon': PIXEL_COLORS['cyan']
            },
            'slow': {
                'primary': (100, 40, 140),
                'secondary': (140, 60, 200),
                'glow': (200, 100, 255),
                'icon': PIXEL_COLORS['purple']
            }
        }

        self.names = {
            'basic': 'БАЗОВАЯ',
            'sniper': 'СНАЙПЕР',
            'slow': 'ЗАМЕДЛЕНИЕ'
        }

        self.descriptions = {
            'basic': 'Сбалансированная',
            'sniper': 'Дальнобойная',
            'slow': 'Замедляет врагов'
        }

    def update(self, mouse_x, mouse_y, is_selected, can_afford):
        self.frame += 1
        self.is_selected = is_selected
        self.can_afford = can_afford

        self.is_hovered = (
                self.x - self.width / 2 <= mouse_x <= self.x + self.width / 2 and
                self.y - self.height / 2 <= mouse_y <= self.y + self.height / 2
        )

        target_hover = 1.0 if self.is_hovered else 0.0
        self.hover_progress += (target_hover - self.hover_progress) * 0.15

        target_select = 1.0 if is_selected else 0.0
        self.select_progress += (target_select - self.select_progress) * 0.2

    def draw(self, ui_particles):
        colors = self.colors[self.tower_type]

        lift = self.hover_progress * 8
        scale = 1.0 + self.hover_progress * 0.05

        draw_y = self.y + lift
        draw_width = self.width * scale
        draw_height = self.height * scale

        shadow_offset = 4 + self.hover_progress * 4
        draw_rectangle_filled(
            self.x + 3, draw_y - shadow_offset,
            draw_width, draw_height,
            (0, 0, 0, int(100 + self.hover_progress * 50))
        )

        if self.select_progress > 0.1:
            glow_size = 10 + math.sin(self.frame * 0.1) * 3
            glow_alpha = int(100 * self.select_progress)
            for i in range(3):
                draw_rectangle_filled(
                    self.x, draw_y,
                    draw_width + glow_size * (i + 1),
                    draw_height + glow_size * (i + 1),
                    (*colors['glow'], int(glow_alpha / (i + 1)))
                )

        if not self.can_afford:
            bg_color = (60, 40, 40, 220)
        elif self.is_selected:
            bg_color = (*colors['primary'], 240)
        elif self.is_hovered:
            bg_color = (*colors['primary'], 200)
        else:
            bg_color = (40, 40, 50, 180)

        draw_rectangle_filled(self.x, draw_y, draw_width, draw_height, bg_color)

        gradient_height = 4
        for i in range(int(gradient_height)):
            alpha = 255 - i * 50
            draw_rectangle_filled(
                self.x, draw_y + draw_height / 2 - i,
                draw_width, 1,
                (*colors['secondary'], alpha)
            )

        if self.is_selected:
            border_color = colors['glow']
            border_width = 3
        elif self.is_hovered:
            border_color = colors['secondary']
            border_width = 2
        else:
            border_color = (80, 80, 100)
            border_width = 1

        draw_rectangle_outline(self.x, draw_y, draw_width, draw_height, border_color, border_width)

        corner_size = 8
        corner_color = colors['secondary'] if (self.is_selected or self.is_hovered) else (60, 60, 80)

        draw_rectangle_filled(self.x - draw_width / 2 + corner_size / 2, draw_y + draw_height / 2 - corner_size / 2,
                              corner_size, 2, corner_color)
        draw_rectangle_filled(self.x - draw_width / 2 + 1, draw_y + draw_height / 2 - corner_size / 2, 2, corner_size,
                              corner_color)
        draw_rectangle_filled(self.x + draw_width / 2 - corner_size / 2, draw_y + draw_height / 2 - corner_size / 2,
                              corner_size, 2, corner_color)
        draw_rectangle_filled(self.x + draw_width / 2 - 1, draw_y + draw_height / 2 - corner_size / 2, 2, corner_size,
                              corner_color)
        draw_rectangle_filled(self.x - draw_width / 2 + corner_size / 2, draw_y - draw_height / 2 + corner_size / 2,
                              corner_size, 2, corner_color)
        draw_rectangle_filled(self.x - draw_width / 2 + 1, draw_y - draw_height / 2 + corner_size / 2, 2, corner_size,
                              corner_color)
        draw_rectangle_filled(self.x + draw_width / 2 - corner_size / 2, draw_y - draw_height / 2 + corner_size / 2,
                              corner_size, 2, corner_color)
        draw_rectangle_filled(self.x + draw_width / 2 - 1, draw_y - draw_height / 2 + corner_size / 2, 2, corner_size,
                              corner_color)

        icon_x = self.x - draw_width / 2 + 30
        icon_y = draw_y + 10
        self.draw_tower_icon(icon_x, icon_y, colors)

        key_x = self.x - draw_width / 2 + 12
        key_y = draw_y + draw_height / 2 - 12
        key_bg_color = colors['secondary'] if self.is_selected else (60, 60, 80)
        draw_rectangle_filled(key_x, key_y, 18, 18, key_bg_color)
        draw_rectangle_outline(key_x, key_y, 18, 18, PIXEL_COLORS['white'], 1)
        arcade.draw_text(self.key, key_x, key_y, PIXEL_COLORS['white'], 10,
                         anchor_x="center", anchor_y="center", bold=True)

        name_color = PIXEL_COLORS['white'] if self.can_afford else PIXEL_COLORS['red']
        arcade.draw_text(
            self.names[self.tower_type],
            self.x + 5, draw_y + 20,
            name_color, 11, anchor_x="center", bold=True
        )

        desc_color = (*colors['secondary'], 200) if self.can_afford else (150, 80, 80)
        arcade.draw_text(
            self.descriptions[self.tower_type],
            self.x + 5, draw_y - 8,
            desc_color, 10, anchor_x="center"
        )

        price_y = draw_y - 25
        price_color = PIXEL_COLORS['gold'] if self.can_afford else PIXEL_COLORS['red']

        coin_x = self.x - 15
        arcade.draw_circle_filled(coin_x, price_y, 8, price_color)
        arcade.draw_circle_filled(coin_x, price_y, 5, (255, 255, 200) if self.can_afford else (180, 100, 100))
        arcade.draw_text("$", coin_x, price_y, (100, 80, 0) if self.can_afford else (100, 50, 50),
                         9, anchor_x="center", anchor_y="center", bold=True)

        arcade.draw_text(
            str(self.cost),
            self.x + 5, price_y,
            price_color, 14, anchor_x="center", anchor_y="center", bold=True
        )

        if self.is_selected:
            indicator_y = draw_y - draw_height / 2 - 8
            pulse = abs(math.sin(self.frame * 0.15)) * 0.3 + 0.7
            arcade.draw_text(
                "▼ ВЫБРАНО ▼",
                self.x, indicator_y,
                (*colors['glow'], int(255 * pulse)), 8, anchor_x="center", bold=True
            )

        if self.is_hovered and self.frame % 8 == 0:
            spark_x = self.x + random.uniform(-draw_width / 2, draw_width / 2)
            spark_y = draw_y + draw_height / 2
            ui_particles.emit_ui_sparkle(spark_x, spark_y, colors['glow'])

    def draw_tower_icon(self, x, y, colors):
        rotation = math.sin(self.frame * 0.05) * 0.3
        pulse = abs(math.sin(self.frame * 0.1)) * 2

        if self.tower_type == 'basic':
            arcade.draw_circle_filled(x, y, 12 + pulse, colors['primary'])
            arcade.draw_circle_filled(x, y, 9, colors['secondary'])

            gun_angle = rotation
            gun_x = x + math.cos(gun_angle) * 14
            gun_y = y + math.sin(gun_angle) * 14
            arcade.draw_line(x, y, gun_x, gun_y, colors['glow'], 4)

        elif self.tower_type == 'sniper':
            draw_rectangle_filled(x, y, 18 + pulse, 18 + pulse, colors['primary'])
            draw_rectangle_filled(x, y, 12, 12, colors['secondary'])

            gun_angle = rotation
            gun_x = x + math.cos(gun_angle) * 20
            gun_y = y + math.sin(gun_angle) * 20
            arcade.draw_line(x, y, gun_x, gun_y, colors['glow'], 3)

            scope_x = x + math.cos(gun_angle) * 10
            scope_y = y + math.sin(gun_angle) * 10 + 5
            draw_rectangle_filled(scope_x, scope_y, 4, 6, PIXEL_COLORS['cyan'])

        else:
            points = []
            for i in range(6):
                angle = (i / 6) * math.pi * 2 + self.frame * 0.03
                r = 10 + (i % 2) * 4 + pulse
                points.append((x + math.cos(angle) * r, y + math.sin(angle) * r))
            arcade.draw_polygon_filled(points, colors['primary'])
            arcade.draw_circle_filled(x, y, 5 + pulse * 0.5, colors['glow'])

            ring_alpha = int(100 + math.sin(self.frame * 0.1) * 50)
            arcade.draw_circle_outline(x, y, 15 + pulse, (*colors['glow'], ring_alpha), 1)

    def contains_point(self, x, y):
        return (
                self.x - self.width / 2 <= x <= self.x + self.width / 2 and
                self.y - self.height / 2 <= y <= self.y + self.height / 2
        )


class StartWaveButton:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 160
        self.height = 70
        self.is_hovered = False
        self.hover_progress = 0.0
        self.frame = 0
        self.is_active = True
        self.click_animation = 0.0

    def update(self, mouse_x, mouse_y, is_active):
        self.frame += 1
        self.is_active = is_active

        self.is_hovered = is_active and (
                self.x - self.width / 2 <= mouse_x <= self.x + self.width / 2 and
                self.y - self.height / 2 <= mouse_y <= self.y + self.height / 2
        )

        target_hover = 1.0 if self.is_hovered else 0.0
        self.hover_progress += (target_hover - self.hover_progress) * 0.15

        self.click_animation = max(0, self.click_animation - 0.1)

    def click(self):
        self.click_animation = 1.0

    def draw(self, ui_particles):
        if not self.is_active:
            return

        pulse = abs(math.sin(self.frame * 0.08)) * 8
        lift = self.hover_progress * 5
        scale = 1.0 + self.hover_progress * 0.08 - self.click_animation * 0.05

        draw_y = self.y + lift
        draw_width = (self.width + pulse) * scale
        draw_height = self.height * scale

        glow_intensity = 0.5 + self.hover_progress * 0.5 + abs(math.sin(self.frame * 0.1)) * 0.2
        for i in range(4):
            glow_alpha = int(60 * glow_intensity / (i + 1))
            draw_rectangle_filled(
                self.x, draw_y,
                draw_width + 15 * (i + 1),
                draw_height + 10 * (i + 1),
                (100, 255, 100, glow_alpha)
            )

        draw_rectangle_filled(
            self.x + 4, draw_y - 4,
            draw_width, draw_height,
            (0, 0, 0, 150)
        )

        gradient_steps = 5
        for i in range(gradient_steps):
            t = i / gradient_steps
            color_r = int(40 + t * 30 + self.hover_progress * 20)
            color_g = int(120 + t * 40 + self.hover_progress * 30)
            color_b = int(40 + t * 30 + self.hover_progress * 20)
            step_height = draw_height / gradient_steps
            step_y = draw_y - draw_height / 2 + step_height * (i + 0.5)
            draw_rectangle_filled(self.x, step_y, draw_width, step_height + 1, (color_r, color_g, color_b))

        border_color = PIXEL_COLORS['white'] if self.is_hovered else PIXEL_COLORS['light_green']
        draw_rectangle_outline(self.x, draw_y, draw_width, draw_height, border_color, 3)

        draw_rectangle_outline(self.x, draw_y, draw_width - 8, draw_height - 8,
                               (*PIXEL_COLORS['green'], 150), 1)

        play_x = self.x - 35
        play_points = [
            (play_x - 8, draw_y - 10),
            (play_x - 8, draw_y + 10),
            (play_x + 10, draw_y)
        ]
        arcade.draw_polygon_filled(play_points, PIXEL_COLORS['white'])

        text_pulse = abs(math.sin(self.frame * 0.1)) * 0.1 + 0.9
        arcade.draw_text(
            "START",
            self.x + 10, draw_y,
            PIXEL_COLORS['white'], int(22 * text_pulse),
            anchor_x="center", anchor_y="center", bold=True
        )

        for i in range(3):
            dot_x = self.x + 50 + i * 8
            dot_alpha = int((math.sin(self.frame * 0.15 + i * 0.5) + 1) * 127)
            arcade.draw_circle_filled(dot_x, draw_y, 3, (*PIXEL_COLORS['white'], dot_alpha))

        if self.is_hovered and self.frame % 5 == 0:
            edge_x = self.x + random.uniform(-draw_width / 2, draw_width / 2)
            edge_y = draw_y + draw_height / 2
            ui_particles.emit_ui_sparkle(edge_x, edge_y, PIXEL_COLORS['light_green'])

    def contains_point(self, x, y):
        return (
                self.x - self.width / 2 <= x <= self.x + self.width / 2 and
                self.y - self.height / 2 <= y <= self.y + self.height / 2
        )


class TopUIPanel:

    def __init__(self):
        self.height = 110
        self.frame = 0
        self.particles = ParticleSystem()

        card_y = SCREEN_HEIGHT - 55
        self.tower_cards = [
            TowerCard(480, card_y, 'basic', '1', 80),
            TowerCard(640, card_y, 'sniper', '2', 250),
            TowerCard(800, card_y, 'slow', '3', 180),
        ]

        self.start_button = StartWaveButton(SCREEN_WIDTH - 100, card_y)

        self.money_display = 0
        self.health_flash = 0
        self.wave_flash = 0

    def update(self, mouse_x, mouse_y, selected_type, money, can_start_wave):
        self.frame += 1
        self.particles.update()

        for card in self.tower_cards:
            can_afford = money >= card.cost
            is_selected = card.tower_type == selected_type
            card.update(mouse_x, mouse_y, is_selected, can_afford)

        self.start_button.update(mouse_x, mouse_y, can_start_wave)

        self.money_display += (money - self.money_display) * 0.15

        self.health_flash = max(0, self.health_flash - 0.05)
        self.wave_flash = max(0, self.wave_flash - 0.03)

    def draw(self, money, base_health, wave, enemies_alive):
        for i in range(self.height):
            t = i / self.height
            alpha = int(220 - t * 40)
            color = (int(25 + t * 10), int(25 + t * 10), int(35 + t * 15), alpha)
            draw_rectangle_filled(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT - i,
                SCREEN_WIDTH, 1, color
            )

        line_y = SCREEN_HEIGHT - self.height
        glow = abs(math.sin(self.frame * 0.05)) * 0.3 + 0.7

        for i in range(5):
            alpha = int(50 * glow / (i + 1))
            draw_rectangle_filled(
                SCREEN_WIDTH // 2, line_y - i,
                SCREEN_WIDTH, 2, (40, 180, 40, alpha)
            )

        arcade.draw_line(0, line_y, SCREEN_WIDTH, line_y, PIXEL_COLORS['green'], 3)

        for x in range(0, SCREEN_WIDTH, 100):
            dot_pulse = abs(math.sin(self.frame * 0.05 + x * 0.01)) * 0.5 + 0.5
            arcade.draw_circle_filled(x, line_y, 4, (*PIXEL_COLORS['light_green'], int(200 * dot_pulse)))

        self.particles.draw()

        self.draw_resources(money, base_health, wave, enemies_alive)

        for card in self.tower_cards:
            card.draw(self.particles)

        sep_x = 350
        arcade.draw_line(sep_x, SCREEN_HEIGHT - 10, sep_x, SCREEN_HEIGHT - self.height + 10,
                         (*PIXEL_COLORS['gray'], 100), 2)

        self.start_button.draw(self.particles)

    def draw_resources(self, money, base_health, wave, enemies_alive):
        money_x = 80
        money_y = SCREEN_HEIGHT - 35

        draw_rectangle_filled(money_x, money_y, 130, 40, (30, 35, 25, 200))
        draw_rectangle_outline(money_x, money_y, 130, 40, PIXEL_COLORS['gold'], 2)

        coin_pulse = abs(math.sin(self.frame * 0.1)) * 2
        coin_x = money_x - 45
        arcade.draw_circle_filled(coin_x, money_y, 14 + coin_pulse, PIXEL_COLORS['gold'])
        arcade.draw_circle_filled(coin_x, money_y, 10, (255, 240, 150))
        arcade.draw_circle_outline(coin_x, money_y, 14 + coin_pulse, (180, 150, 0), 2)
        arcade.draw_text("$", coin_x, money_y, (150, 120, 0), 12,
                         anchor_x="center", anchor_y="center", bold=True)

        display_money = int(self.money_display)
        money_color = PIXEL_COLORS['gold']
        if abs(money - self.money_display) > 5:
            money_color = PIXEL_COLORS['white']

        arcade.draw_text(
            f"{display_money}",
            money_x + 10, money_y,
            money_color, 22, anchor_x="center", anchor_y="center", bold=True
        )

        health_x = 80
        health_y = SCREEN_HEIGHT - 80

        health_bg_color = (40, 25, 25, 200) if base_health <= 1 else (30, 30, 35, 200)
        draw_rectangle_filled(health_x, health_y, 130, 35, health_bg_color)

        if base_health > 2:
            health_color = PIXEL_COLORS['green']
            heart_color = (255, 100, 100)
        elif base_health > 1:
            health_color = PIXEL_COLORS['yellow']
            heart_color = (255, 150, 50)
        else:
            health_color = PIXEL_COLORS['red']
            heart_color = (255, 50, 50)
            if self.frame % 30 < 15:
                health_bg_color = (60, 30, 30, 220)
                draw_rectangle_filled(health_x, health_y, 130, 35, health_bg_color)

        draw_rectangle_outline(health_x, health_y, 130, 35, health_color, 2)

        heart_x = health_x - 45
        heart_beat = abs(math.sin(self.frame * 0.15)) * 2

        arcade.draw_circle_filled(heart_x - 4, health_y + 2, 6 + heart_beat, heart_color)
        arcade.draw_circle_filled(heart_x + 4, health_y + 2, 6 + heart_beat, heart_color)
        heart_points = [
            (heart_x - 10 - heart_beat, health_y + 2),
            (heart_x + 10 + heart_beat, health_y + 2),
            (heart_x, health_y - 10 - heart_beat)
        ]
        arcade.draw_polygon_filled(heart_points, heart_color)

        arcade.draw_text(
            f"HP: {base_health}",
            health_x + 10, health_y,
            health_color, 16, anchor_x="center", anchor_y="center", bold=True
        )

        wave_x = 230
        wave_y = SCREEN_HEIGHT - 55

        wave_bg_alpha = int(200 + self.wave_flash * 55)
        draw_rectangle_filled(wave_x, wave_y, 100, 70, (25, 35, 40, min(255, wave_bg_alpha)))
        draw_rectangle_outline(wave_x, wave_y, 100, 70, PIXEL_COLORS['cyan'], 2)

        wave_icon_x = wave_x
        wave_icon_y = wave_y + 15
        for i in range(3):
            wave_offset = math.sin(self.frame * 0.1 + i * 0.5) * 3
            line_y = wave_icon_y - i * 6 + wave_offset
            line_width = 30 - i * 5
            line_alpha = 255 - i * 50
            arcade.draw_line(
                wave_icon_x - line_width / 2, line_y,
                wave_icon_x + line_width / 2, line_y,
                (*PIXEL_COLORS['cyan'], line_alpha), 2
            )

        arcade.draw_text(
            f"ВОЛНА",
            wave_x, wave_y - 5,
            PIXEL_COLORS['gray'], 9, anchor_x="center", bold=True
        )

        wave_text_scale = 1.0 + self.wave_flash * 0.3
        arcade.draw_text(
            f"{wave}",
            wave_x, wave_y - 20,
            PIXEL_COLORS['cyan'], int(20 * wave_text_scale), anchor_x="center", bold=True
        )

        if enemies_alive > 0:
            arcade.draw_text(
                f"⚔ {enemies_alive}",
                wave_x, wave_y - 45,
                PIXEL_COLORS['red'], 10, anchor_x="center"
            )

    def trigger_wave_flash(self):
        self.wave_flash = 1.0

    def trigger_health_flash(self):
        self.health_flash = 1.0

    def get_clicked_tower_type(self, x, y):
        for card in self.tower_cards:
            if card.contains_point(x, y):
                return card.tower_type
        return None

    def is_start_button_clicked(self, x, y):
        return self.start_button.is_active and self.start_button.contains_point(x, y)


class PixelArt:

    @staticmethod
    def draw_pixel_rect(x, y, width, height, color, outline_color=None):
        draw_rectangle_filled(x, y, width, height, color)
        if outline_color:
            pixel = 2
            draw_rectangle_filled(x, y + height // 2, width, pixel, outline_color)
            draw_rectangle_filled(x, y - height // 2, width, pixel, outline_color)
            draw_rectangle_filled(x - width // 2, y, pixel, height, outline_color)
            draw_rectangle_filled(x + width // 2, y, pixel, height, outline_color)

    @staticmethod
    def draw_pixel_circle(x, y, radius, color, segments=8):
        points = []
        for i in range(segments):
            angle = (i / segments) * math.pi * 2
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            points.append((px, py))
        arcade.draw_polygon_filled(points, color)

    @staticmethod
    def draw_enemy_normal(x, y, size, health_percent, frame, hit_flash=0):
        breathe = math.sin(frame * 0.15) * 2
        bob = math.sin(frame * 0.2) * 1.5

        flash_intensity = min(1.0, hit_flash / 10) if hit_flash > 0 else 0

        draw_rectangle_filled(x, y - size * 0.4, size * 0.8, 4, (20, 20, 20, 100))

        body_colors = [(100, 30, 30), (140, 40, 40), (180, 50, 50)]
        for i, color in enumerate(body_colors):
            layer_size = size - i * 4 + breathe
            if flash_intensity > 0:
                color = (
                    min(255, int(color[0] + (255 - color[0]) * flash_intensity)),
                    min(255, int(color[1] + (100 - color[1]) * flash_intensity)),
                    min(255, int(color[2] + (100 - color[2]) * flash_intensity))
                )
            draw_rectangle_filled(x, y + bob, layer_size, layer_size * 0.9, color)

        horn_color = (60, 20, 20)
        draw_rectangle_filled(x - size * 0.35, y + size * 0.4 + bob, 5, 12, horn_color)
        draw_rectangle_filled(x + size * 0.35, y + size * 0.4 + bob, 5, 12, horn_color)
        draw_rectangle_filled(x - size * 0.35, y + size * 0.55 + bob, 5, 5, horn_color)
        draw_rectangle_filled(x + size * 0.35, y + size * 0.55 + bob, 5, 5, horn_color)

        draw_rectangle_filled(x, y + size * 0.1 + bob, size * 0.7, size * 0.4, (40, 15, 15))

        eye_glow = abs(math.sin(frame * 0.1)) * 0.3 + 0.7
        eye_color = (int(255 * eye_glow), int(100 * eye_glow), 0)

        eye_open = (frame % 90) > 8
        if eye_open:
            draw_rectangle_filled(x - size * 0.18, y + size * 0.15 + bob, 8, 6, (255, 200, 150))
            draw_rectangle_filled(x + size * 0.18, y + size * 0.15 + bob, 8, 6, (255, 200, 150))
            draw_rectangle_filled(x - size * 0.18, y + size * 0.15 + bob, 4, 5, eye_color)
            draw_rectangle_filled(x + size * 0.18, y + size * 0.15 + bob, 4, 5, eye_color)
        else:
            draw_rectangle_filled(x - size * 0.18, y + size * 0.15 + bob, 8, 2, (40, 15, 15))
            draw_rectangle_filled(x + size * 0.18, y + size * 0.15 + bob, 8, 2, (40, 15, 15))

        draw_rectangle_filled(x, y - size * 0.1 + bob, size * 0.4, 4, (20, 5, 5))
        for i in range(3):
            tooth_x = x - 6 + i * 6
            draw_rectangle_filled(tooth_x, y - size * 0.1 + bob, 3, 5, (240, 230, 200))

        leg_anim = math.sin(frame * 0.25) * 4
        draw_rectangle_filled(x - size * 0.25, y - size * 0.55 + leg_anim, 8, 10, (100, 30, 30))
        draw_rectangle_filled(x + size * 0.25, y - size * 0.55 - leg_anim, 8, 10, (100, 30, 30))
        draw_rectangle_filled(x - size * 0.25, y - size * 0.65 + leg_anim, 10, 4, (60, 20, 20))
        draw_rectangle_filled(x + size * 0.25, y - size * 0.65 - leg_anim, 10, 4, (60, 20, 20))

    @staticmethod
    def draw_enemy_fast(x, y, size, health_percent, frame, hit_flash=0):
        flicker = 0.7 + math.sin(frame * 0.5) * 0.3
        alpha = int(200 * flicker)

        flash_intensity = min(1.0, hit_flash / 10) if hit_flash > 0 else 0

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

        draw_rectangle_filled(x + 3, y - 3, size * 0.6, size * 0.3, (20, 60, 80, 60))

        for i in range(4):
            tail_offset = math.sin(frame * 0.3 + i * 0.8) * 4
            tail_y = y - size * 0.3 - i * 6
            tail_alpha = alpha - i * 40
            if tail_alpha > 0:
                tail_width = size * 0.4 - i * 3
                draw_rectangle_filled(x + tail_offset, tail_y, tail_width, 5,
                                      (40, 150, 200, tail_alpha))

        draw_rectangle_filled(x, y - size * 0.15, size * 0.5, size * 0.4, body_color)
        draw_rectangle_filled(x, y + size * 0.2, size * 0.7, size * 0.5, body_color)
        draw_rectangle_filled(x, y + size * 0.45, size * 0.5, size * 0.2, body_color)

        core_pulse = abs(math.sin(frame * 0.2)) * 3
        draw_rectangle_filled(x, y + size * 0.1, size * 0.35 + core_pulse,
                              size * 0.35 + core_pulse, core_color)

        eye_y = y + size * 0.25
        draw_rectangle_filled(x - size * 0.18, eye_y, 10, 12, (0, 40, 60, alpha))
        draw_rectangle_filled(x + size * 0.18, eye_y, 10, 12, (0, 40, 60, alpha))
        eye_glow = abs(math.sin(frame * 0.15)) * 50 + 200
        draw_rectangle_filled(x - size * 0.18, eye_y, 6, 8, (eye_glow, 255, 255, alpha))
        draw_rectangle_filled(x + size * 0.18, eye_y, 6, 8, (eye_glow, 255, 255, alpha))

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
        step = abs(math.sin(frame * 0.08)) * 3
        shake = math.sin(frame * 0.15) * 1

        flash_intensity = min(1.0, hit_flash / 10) if hit_flash > 0 else 0

        draw_rectangle_filled(x + 4, y - size * 0.5, size * 0.9, 8, (20, 20, 20, 80))

        leg_color = (50, 50, 60)
        leg_anim = math.sin(frame * 0.1) * 2
        draw_rectangle_filled(x - size * 0.3, y - size * 0.55 - leg_anim, 14, 20, leg_color)
        draw_rectangle_filled(x - size * 0.3, y - size * 0.7 - leg_anim, 18, 8, (40, 40, 50))
        draw_rectangle_filled(x + size * 0.3, y - size * 0.55 + leg_anim, 14, 20, leg_color)
        draw_rectangle_filled(x + size * 0.3, y - size * 0.7 + leg_anim, 18, 8, (40, 40, 50))

        body_y = y + step

        def apply_flash(color):
            if flash_intensity > 0:
                return (
                    min(255, int(color[0] + (255 - color[0]) * flash_intensity)),
                    min(255, int(color[1] + (100 - color[1]) * flash_intensity)),
                    min(255, int(color[2] + (100 - color[2]) * flash_intensity))
                )
            return color

        draw_rectangle_filled(x + shake, body_y - size * 0.2, size * 1.1, size * 0.4, apply_flash((60, 60, 70)))
        draw_rectangle_filled(x + shake, body_y, size * 1.0, size * 0.6, apply_flash((80, 80, 95)))
        draw_rectangle_filled(x + shake, body_y + size * 0.25, size * 0.9, size * 0.35, apply_flash((100, 100, 115)))

        plate_color = apply_flash((50, 50, 60))
        for i in range(4):
            plate_y = body_y - size * 0.3 + i * (size * 0.2)
            draw_rectangle_filled(x + shake, plate_y, size * 0.95, 3, plate_color)

        rivet_color = apply_flash((120, 120, 130))
        for i in range(3):
            for j in range(2):
                rivet_x = x - size * 0.35 + j * size * 0.7 + shake
                rivet_y = body_y - size * 0.2 + i * size * 0.25
                draw_rectangle_filled(rivet_x, rivet_y, 4, 4, rivet_color)

        draw_rectangle_filled(x - size * 0.5 + shake, body_y + size * 0.1, 12, 20, apply_flash((70, 70, 80)))
        draw_rectangle_filled(x + size * 0.5 + shake, body_y + size * 0.1, 12, 20, apply_flash((70, 70, 80)))

        head_y = body_y + size * 0.45
        draw_rectangle_filled(x + shake, head_y, size * 0.5, size * 0.3, apply_flash((90, 90, 100)))
        draw_rectangle_filled(x + shake, head_y + size * 0.1, size * 0.4, size * 0.15, apply_flash((70, 70, 80)))

        visor_glow = abs(math.sin(frame * 0.12)) * 0.5 + 0.5
        visor_color = (int(200 * visor_glow), int(40 * visor_glow), int(40 * visor_glow))
        draw_rectangle_filled(x + shake, head_y, size * 0.4, 6, (20, 0, 0))
        draw_rectangle_filled(x + shake, head_y, size * 0.35, 4, visor_color)

        if visor_glow > 0.7:
            draw_rectangle_filled(x + shake, head_y, size * 0.45, 8, (*visor_color, 50))

        if health_percent < 1.0:
            if health_percent < 0.5:
                crack_color = (40, 40, 45)
                draw_rectangle_filled(x - size * 0.2 + shake, body_y + size * 0.1, 2, 15, crack_color)
                draw_rectangle_filled(x + size * 0.15 + shake, body_y - size * 0.1, 2, 20, crack_color)
            if health_percent < 0.25:
                if frame % 10 < 5:
                    spark_x = x + random.randint(-int(size * 0.3), int(size * 0.3))
                    spark_y = body_y + random.randint(-int(size * 0.2), int(size * 0.2))
                    draw_rectangle_filled(spark_x, spark_y, 3, 3, (255, 200, 50))

    # ============ УЛУЧШЕННЫЕ ТУРЕЛИ ============

    @staticmethod
    def draw_tower_basic(x, y, angle, level, frame):

        # Тень
        draw_rectangle_filled(x + 3, y - 3, 36, 36, (0, 0, 0, 60))

        # Основание - многослойное
        # Нижний слой (опора)
        for i in range(3):
            layer_size = 20 - i * 2
            layer_color = (
                30 + i * 10 + level * 5,
                50 + i * 15 + level * 8,
                30 + i * 10 + level * 5
            )
            PixelArt.draw_pixel_circle(x, y, layer_size, layer_color, 8)

        # Металлическое кольцо
        arcade.draw_circle_outline(x, y, 16, PIXEL_COLORS['dark_metal'], 2)

        # Вращающаяся платформа
        platform_pulse = abs(math.sin(frame * 0.05)) * 1
        PixelArt.draw_pixel_circle(x, y, 12 + platform_pulse, PIXEL_COLORS['metal'], 8)

        # Заклёпки на платформе
        for i in range(4):
            rivet_angle = (i / 4) * math.pi * 2 + frame * 0.01
            rivet_x = x + math.cos(rivet_angle) * 9
            rivet_y = y + math.sin(rivet_angle) * 9
            draw_rectangle_filled(rivet_x, rivet_y, 3, 3, PIXEL_COLORS['dark_metal'])

        # Пушка
        gun_length = 22 + level * 4
        gun_width = 7 + level

        # Откат при стрельбе (анимация)
        recoil = abs(math.sin(frame * 0.3)) * 2 if frame % 60 < 10 else 0

        # Ствол пушки - многослойный
        end_x = x + math.cos(angle) * (gun_length - recoil)
        end_y = y + math.sin(angle) * (gun_length - recoil)

        # Основание ствола
        base_x = x + math.cos(angle) * 5
        base_y = y + math.sin(angle) * 5

        # Тело ствола
        for i in range(6):
            t = i / 6
            px = base_x + (end_x - base_x) * t
            py = base_y + (end_y - base_y) * t
            width = gun_width - t * 2

            # Градиент цвета
            color = (
                int(40 + t * 20),
                int(70 + t * 30),
                int(40 + t * 20)
            )
            draw_rectangle_filled(px, py, width, width, color)

        # Дуло с бликом
        draw_rectangle_filled(end_x, end_y, gun_width - 1, gun_width - 1, PIXEL_COLORS['dark_green'])
        muzzle_glow = abs(math.sin(frame * 0.1)) * 0.3 + 0.7
        draw_rectangle_filled(end_x, end_y, gun_width - 3, gun_width - 3,
                              (int(80 * muzzle_glow), int(150 * muzzle_glow), int(80 * muzzle_glow)))

        # Усиления на стволе
        for i in range(2):
            reinforce_t = 0.3 + i * 0.35
            rx = base_x + (end_x - base_x) * reinforce_t
            ry = base_y + (end_y - base_y) * reinforce_t
            draw_rectangle_filled(rx, ry, gun_width + 2, 3, PIXEL_COLORS['dark_metal'])

        # Прицельное устройство
        sight_x = x + math.cos(angle) * 12
        sight_y = y + math.sin(angle) * 12
        perp_angle = angle + math.pi / 2
        sight_offset = 5
        draw_rectangle_filled(
            sight_x + math.cos(perp_angle) * sight_offset,
            sight_y + math.sin(perp_angle) * sight_offset,
            3, 6, PIXEL_COLORS['metal']
        )

        # Индикатор уровня - звёзды
        for i in range(level):
            star_x = x - 12 + i * 10
            star_y = y - 24
            arcade.draw_circle_filled(star_x, star_y, 4, PIXEL_COLORS['gold'])
            arcade.draw_circle_filled(star_x, star_y, 2, PIXEL_COLORS['yellow'])

    @staticmethod
    def draw_tower_sniper(x, y, angle, level, frame):
        # Тень
        draw_rectangle_filled(x + 4, y - 4, 34, 34, (0, 0, 0, 70))

        # Основание - техно-стиль
        # Внешний квадрат
        draw_rectangle_filled(x, y, 32, 32, PIXEL_COLORS['dark_blue'])
        draw_rectangle_outline(x, y, 32, 32, PIXEL_COLORS['cyan'], 2)

        # Внутренняя структура
        draw_rectangle_filled(x, y, 24, 24, (30, 60, 120))

        # Диагональные линии (техно-узор)
        for i in range(-2, 3):
            line_offset = i * 6
            arcade.draw_line(
                x - 10 + line_offset, y - 10,
                x + 10 + line_offset, y + 10,
                (*PIXEL_COLORS['cyan'], 60), 1
            )

        # Вращающееся ядро
        core_angle = frame * 0.03
        for i in range(4):
            dot_angle = core_angle + (i / 4) * math.pi * 2
            dot_x = x + math.cos(dot_angle) * 8
            dot_y = y + math.sin(dot_angle) * 8
            glow = abs(math.sin(frame * 0.1 + i)) * 0.5 + 0.5
            arcade.draw_circle_filled(dot_x, dot_y, 3, (*PIXEL_COLORS['cyan'], int(200 * glow)))

        # Центральный элемент
        PixelArt.draw_pixel_circle(x, y, 6, (40, 80, 160), 6)

        # Длинный снайперский ствол
        gun_length = 35 + level * 6
        gun_width = 4 + level // 2

        end_x = x + math.cos(angle) * gun_length
        end_y = y + math.sin(angle) * gun_length

        # Ствол с градиентом
        segments = 10
        for i in range(segments):
            t = i / segments
            px = x + (end_x - x) * t
            py = y + (end_y - y) * t

            # Пульсация энергии по стволу
            energy_pulse = abs(math.sin(frame * 0.15 - t * 3)) * 0.3

            color = (
                int(40 + energy_pulse * 100),
                int(80 + energy_pulse * 150),
                int(160 + energy_pulse * 50)
            )

            width = gun_width + (1 - t) * 2
            draw_rectangle_filled(px, py, width, width, color)

        # Энергетические кольца на стволе
        for i in range(3):
            ring_t = 0.25 + i * 0.25
            ring_x = x + (end_x - x) * ring_t
            ring_y = y + (end_y - y) * ring_t
            ring_pulse = abs(math.sin(frame * 0.1 + i * 0.5))
            arcade.draw_circle_outline(ring_x, ring_y, 5, (*PIXEL_COLORS['cyan'], int(150 * ring_pulse)), 1)

        # Оптический прицел (сложный)
        scope_t = 0.4
        scope_x = x + (end_x - x) * scope_t
        scope_y = y + (end_y - y) * scope_t
        perp_angle = angle + math.pi / 2

        # Корпус прицела
        scope_body_x = scope_x + math.cos(perp_angle) * 8
        scope_body_y = scope_y + math.sin(perp_angle) * 8
        draw_rectangle_filled(scope_body_x, scope_body_y, 8, 12, PIXEL_COLORS['dark_metal'])
        draw_rectangle_filled(scope_body_x, scope_body_y, 5, 10, PIXEL_COLORS['metal'])

        # Линза прицела (светится)
        lens_glow = abs(math.sin(frame * 0.08)) * 0.5 + 0.5
        arcade.draw_circle_filled(scope_body_x, scope_body_y + 4, 3,
                                  (int(100 * lens_glow), int(200 * lens_glow), int(255 * lens_glow)))

        # Лазерный прицел
        if frame % 3 < 2:
            laser_length = 80 + level * 20
            laser_end_x = x + math.cos(angle) * laser_length
            laser_end_y = y + math.sin(angle) * laser_length

            # Несколько слоёв лазера
            for i in range(3):
                alpha = 80 - i * 25
                width = 3 - i
                arcade.draw_line(end_x, end_y, laser_end_x, laser_end_y,
                                 (*PIXEL_COLORS['cyan'], alpha), width)

        # Дуло с энергетическим эффектом
        muzzle_glow = abs(math.sin(frame * 0.2)) * 100 + 100
        arcade.draw_circle_filled(end_x, end_y, 4, (muzzle_glow, muzzle_glow, 255))
        arcade.draw_circle_filled(end_x, end_y, 2, PIXEL_COLORS['white'])

        # Индикатор уровня - энергетические ячейки
        for i in range(level):
            cell_x = x - 14 + i * 12
            cell_y = y - 22
            draw_rectangle_filled(cell_x, cell_y, 8, 5, PIXEL_COLORS['dark_blue'])
            cell_fill = abs(math.sin(frame * 0.1 + i * 0.5)) * 0.3 + 0.7
            draw_rectangle_filled(cell_x, cell_y, int(6 * cell_fill), 3, PIXEL_COLORS['cyan'])

    @staticmethod
    def draw_tower_slow(x, y, angle, level, frame):

        # Магическое свечение под турелью
        glow_pulse = abs(math.sin(frame * 0.08)) * 0.5 + 0.5
        for i in range(4):
            glow_r = 25 + i * 8 + glow_pulse * 5
            glow_alpha = int(60 - i * 15)
            arcade.draw_circle_filled(x, y, glow_r, (*PIXEL_COLORS['purple'], glow_alpha))

        # Тень
        draw_rectangle_filled(x + 2, y - 4, 30, 20, (0, 0, 0, 50))

        # Основание - магический круг
        arcade.draw_circle_filled(x, y - 5, 15, PIXEL_COLORS['dark_purple'])
        arcade.draw_circle_outline(x, y - 5, 15, PIXEL_COLORS['purple'], 2)

        # Руны на основании
        rune_count = 6
        for i in range(rune_count):
            rune_angle = (i / rune_count) * math.pi * 2 + frame * 0.02
            rune_x = x + math.cos(rune_angle) * 11
            rune_y = y - 5 + math.sin(rune_angle) * 11
            rune_alpha = int(abs(math.sin(frame * 0.1 + i)) * 200 + 55)
            draw_rectangle_filled(rune_x, rune_y, 3, 3, (*PIXEL_COLORS['pink'], rune_alpha))

        # Парящий кристалл
        float_offset = math.sin(frame * 0.1) * 4
        crystal_y = y + 8 + float_offset

        # Кристалл - многогранник
        crystal_size = 14 + level * 2
        crystal_rotation = frame * 0.03

        # Внешние грани кристалла
        points_outer = []
        for i in range(6):
            a = (i / 6) * math.pi * 2 + crystal_rotation
            r = crystal_size + (i % 2) * 5
            points_outer.append((x + math.cos(a) * r, crystal_y + math.sin(a) * r))

        # Тень кристалла
        shadow_points = [(p[0] + 2, p[1] - 3) for p in points_outer]
        arcade.draw_polygon_filled(shadow_points, (0, 0, 0, 40))

        # Внешний слой кристалла
        arcade.draw_polygon_filled(points_outer, (100, 40, 140))
        arcade.draw_polygon_outline(points_outer, PIXEL_COLORS['pink'], 2)

        # Внутренний кристалл
        points_inner = []
        for i in range(6):
            a = (i / 6) * math.pi * 2 + crystal_rotation + 0.3
            r = crystal_size * 0.6 + (i % 2) * 3
            points_inner.append((x + math.cos(a) * r, crystal_y + math.sin(a) * r))
        arcade.draw_polygon_filled(points_inner, (140, 60, 200))

        # Ядро кристалла (пульсирующее)
        core_pulse = abs(math.sin(frame * 0.15)) * 4 + 4
        core_color_intensity = abs(math.sin(frame * 0.1))
        core_color = (
            int(200 + core_color_intensity * 55),
            int(100 + core_color_intensity * 100),
            int(255)
        )
        arcade.draw_circle_filled(x, crystal_y, core_pulse, core_color)
        arcade.draw_circle_filled(x, crystal_y, core_pulse * 0.5, PIXEL_COLORS['white'])

        # Энергетические лучи от кристалла
        ray_count = 4 + level
        for i in range(ray_count):
            ray_angle = (i / ray_count) * math.pi * 2 + frame * 0.05
            ray_length = 20 + abs(math.sin(frame * 0.1 + i)) * 10
            ray_end_x = x + math.cos(ray_angle) * ray_length
            ray_end_y = crystal_y + math.sin(ray_angle) * ray_length
            ray_alpha = int(abs(math.sin(frame * 0.15 + i * 0.7)) * 150 + 50)
            arcade.draw_line(x, crystal_y, ray_end_x, ray_end_y,
                             (*PIXEL_COLORS['cyan'], ray_alpha), 2)

        # Орбитальные частицы
        for i in range(3 + level):
            orbit_angle = frame * 0.08 + (i / (3 + level)) * math.pi * 2
            orbit_r = 22 + i * 3
            orbit_x = x + math.cos(orbit_angle) * orbit_r
            orbit_y = crystal_y + math.sin(orbit_angle) * orbit_r * 0.5  # Эллипс
            particle_alpha = int(abs(math.sin(frame * 0.2 + i)) * 200 + 55)
            arcade.draw_circle_filled(orbit_x, orbit_y, 3, (*PIXEL_COLORS['pink'], particle_alpha))

        # Замедляющие волны (расходящиеся кольца)
        wave_count = 2
        for i in range(wave_count):
            wave_progress = ((frame * 0.02 + i * 0.5) % 1.0)
            wave_r = 15 + wave_progress * 40
            wave_alpha = int((1 - wave_progress) * 100)
            if wave_alpha > 10:
                arcade.draw_circle_outline(x, y, wave_r, (*PIXEL_COLORS['cyan'], wave_alpha), 2)

        # Индикатор уровня - магические символы
        for i in range(level):
            symbol_x = x - 10 + i * 10
            symbol_y = y - 28
            symbol_pulse = abs(math.sin(frame * 0.15 + i * 0.8))
            arcade.draw_circle_filled(symbol_x, symbol_y, 4,
                                      (*PIXEL_COLORS['purple'], int(150 + symbol_pulse * 105)))
            arcade.draw_circle_filled(symbol_x, symbol_y, 2, PIXEL_COLORS['pink'])


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
            self.bullet_size = 6
        elif bullet_type == "slow":
            self.color = PIXEL_COLORS['purple']
            self.bullet_size = 8
        else:
            self.color = PIXEL_COLORS['yellow']
            self.bullet_size = 5

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
            self.target.hit_flash_timer = 10
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

        self.trail_timer += 1
        if self.trail_timer % 2 == 0 and particles:
            particles.emit_trail(self.center_x, self.center_y, self.color)

        return False

    def draw(self):
        draw_rectangle_filled(
            self.center_x, self.center_y,
            self.bullet_size, self.bullet_size, self.color
        )
        draw_rectangle_filled(
            self.center_x, self.center_y,
            self.bullet_size + 2, self.bullet_size + 2, (*self.color[:3], 100)
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
            self.max_health = 150  # Увеличено (было 120)
            self.speed = 2.5  # Немного медленнее (было 2.8)
            self.reward = 12  # Уменьшено (было 15)
            self.enemy_size = 20
        elif enemy_type == "tank":
            self.max_health = 800  # Увеличено (было 600)
            self.speed = 0.6  # Медленнее (было 0.7)
            self.reward = 45  # Уменьшено (было 60)
            self.enemy_size = 35
        else:
            self.max_health = 220  # Увеличено (было 180)
            self.speed = 1.3  # Медленнее (было 1.5)
            self.reward = 18  # Уменьшено (было 25)
            self.enemy_size = 25

        self.health = self.max_health
        self.slow_factor = 1.0
        self.width = self.enemy_size
        self.height = self.enemy_size
        self.hit_flash_timer = 0

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

            if self.slow_factor < 1.0 and particles and self.frame % 5 == 0:
                particles.emit_trail(self.center_x, self.center_y, PIXEL_COLORS['cyan'])

        self.slow_factor = min(1.0, self.slow_factor + 0.02)

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1

    def draw(self):
        if self.dead:
            return

        health_percent = self.health / self.max_health

        if self.enemy_type == "fast":
            PixelArt.draw_enemy_fast(self.center_x, self.center_y, self.enemy_size, health_percent, self.frame,
                                     self.hit_flash_timer)
        elif self.enemy_type == "tank":
            PixelArt.draw_enemy_tank(self.center_x, self.center_y, self.enemy_size, health_percent, self.frame,
                                     self.hit_flash_timer)
        else:
            PixelArt.draw_enemy_normal(self.center_x, self.center_y, self.enemy_size, health_percent, self.frame,
                                       self.hit_flash_timer)

        bar_width = self.enemy_size
        bar_height = 4
        bar_y = self.center_y + self.enemy_size / 2 + 10

        draw_rectangle_filled(
            self.center_x, bar_y, bar_width + 2, bar_height + 2, PIXEL_COLORS['black']
        )
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

        # НЕРФНУТЫЕ ПАРАМЕТРЫ ТУРЕЛЕЙ
        if tower_type == "sniper":
            self.range = 220  # Уменьшено (было 250)
            self.damage = 60  # Уменьшено (было 80)
            self.fire_rate = 110  # Медленнее (было 90)
            self.cost = 250  # Дороже (было 200)
            self.upgrade_cost = 200  # Дороже (было 150)
        elif tower_type == "slow":
            self.range = 130  # Уменьшено (было 150)
            self.damage = 8  # Уменьшено (было 10)
            self.fire_rate = 40  # Медленнее (было 30)
            self.cost = 180  # Дороже (было 150)
            self.upgrade_cost = 140  # Дороже (было 100)
            self.slow_effect = 0.5  # Слабее (было 0.4)
        else:  # basic
            self.range = 180
            self.damage = 32
            self.fire_rate = 55
            self.cost = 80
            self.upgrade_cost = 100

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

        if particles:
            muzzle_x = self.center_x + math.cos(self.angle) * 20
            muzzle_y = self.center_y + math.sin(self.angle) * 20
            particles.emit_muzzle_flash(muzzle_x, muzzle_y, self.angle)

        if self.tower_type == "slow" and self.target:
            self.target.slow_factor = self.slow_effect

        bullet_type = self.tower_type if self.tower_type in ["sniper", "slow"] else "normal"
        return Bullet(self.center_x, self.center_y, self.target, self.damage,
                      speed=10 if self.tower_type == "sniper" else 7, bullet_type=bullet_type)

    def upgrade(self):
        self.level += 1
        self.damage = int(self.damage * 1.15)  # Слабее (было 1.2)
        self.range = int(self.range * 1.03)  # Слабее (было 1.05)
        self.fire_rate = int(self.fire_rate * 0.95)  # Слабее (было 0.93)
        self.upgrade_cost = int(self.upgrade_cost * 1.8)  # Дороже (было 1.6)

    def draw(self, selected=False):
        if self.tower_type == "basic":
            PixelArt.draw_tower_basic(self.center_x, self.center_y, self.angle, self.level, self.frame)
        elif self.tower_type == "sniper":
            PixelArt.draw_tower_sniper(self.center_x, self.center_y, self.angle, self.level, self.frame)
        else:
            PixelArt.draw_tower_slow(self.center_x, self.center_y, self.angle, self.level, self.frame)

        if selected:
            draw_rectangle_outline(self.center_x, self.center_y, 50, 50,
                                   PIXEL_COLORS['yellow'], 2)


class WaveManager:
    def __init__(self):
        self.wave = 0
        self.active = False
        self.spawn_timer = 0
        self.spawn_interval = 45  # Быстрее спавн (было 50)
        self.enemies_to_spawn = []
        self.wave_text_timer = 0

    def start_wave(self):
        self.wave += 1
        self.active = True
        self.spawn_timer = 0
        self.wave_text_timer = 120

        try:
            sound = arcade.load_sound("lvl_up.wav")
            arcade.play_sound(sound)
        except Exception:
            pass

        # Больше врагов за волну
        enemy_count = 1 + self.wave * 2  # Увеличено (было 5 + wave * 3)
        self.enemies_to_spawn = []

        for i in range(enemy_count):
            if self.wave >= 4 and random.random() < 0.15:  # Танки раньше появляются
                self.enemies_to_spawn.append("tank")
            elif random.random() < 0.35:  # Больше быстрых
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

    def __init__(self):
        self.frame = 0
        self.particles = ParticleSystem()
        self.selected_option = 0
        self.options = ["НАЧАТЬ ИГРУ", "УПРАВЛЕНИЕ", "ВЫХОД"]
        self.show_controls = False

    def update(self):
        self.frame += 1
        self.particles.update()

        if self.frame % 10 == 0:
            x = random.randint(0, SCREEN_WIDTH)
            self.particles.emit_anomaly(x, random.randint(100, 700))

    def draw(self):
        for y in range(0, SCREEN_HEIGHT, 4):
            color_val = int(20 + (y / SCREEN_HEIGHT) * 30)
            draw_rectangle_filled(
                SCREEN_WIDTH // 2, y, SCREEN_WIDTH, 4,
                (color_val, color_val + 10, color_val)
            )

        for x in range(0, SCREEN_WIDTH, 40):
            alpha = int(50 + math.sin(self.frame * 0.02 + x * 0.01) * 20)
            arcade.draw_line(x, 0, x, SCREEN_HEIGHT, (40, 60, 40, alpha), 1)
        for y in range(0, SCREEN_HEIGHT, 40):
            alpha = int(50 + math.sin(self.frame * 0.02 + y * 0.01) * 20)
            arcade.draw_line(0, y, SCREEN_WIDTH, y, (40, 60, 40, alpha), 1)

        self.particles.draw()

        title = "🛡 Iron Path: Tower Defense"
        glitch_offset = random.randint(-2, 2) if random.random() < 0.1 else 0

        arcade.draw_text(title, SCREEN_WIDTH // 2 + 4 + glitch_offset,
                         SCREEN_HEIGHT - 150 - 4, PIXEL_COLORS['black'],
                         48, anchor_x="center", bold=True)

        arcade.draw_text(title, SCREEN_WIDTH // 2 + glitch_offset,
                         SCREEN_HEIGHT - 150, PIXEL_COLORS['green'],
                         48, anchor_x="center", bold=True)

        subtitle = "DEFEND THE IRON PATH"
        arcade.draw_text(subtitle, SCREEN_WIDTH // 2,
                         SCREEN_HEIGHT - 200, PIXEL_COLORS['cyan'],
                         24, anchor_x="center")

        if self.show_controls:
            self.draw_controls()
        else:
            for i, option in enumerate(self.options):
                y = SCREEN_HEIGHT // 2 - i * 60

                if i == self.selected_option:
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

        hint_alpha = int(abs(math.sin(self.frame * 0.05)) * 200) + 55
        arcade.draw_text("↑↓ - ВЫБОР   ENTER - ПОДТВЕРДИТЬ",
                         SCREEN_WIDTH // 2, 50, (*PIXEL_COLORS['gray'], hint_alpha),
                         16, anchor_x="center")

    def draw_controls(self):
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
            "BASIC - Сбалансированная ($80)",
            "SNIPER - Дальнобойная ($250)",
            "SLOW - Замедляющая ($180)",
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

        self.state = "menu"
        self.main_menu = MainMenu()

        self.reset_game()

    def reset_game(self):
        self.towers = []
        self.enemies = arcade.SpriteList()
        self.bullets = arcade.SpriteList()
        self.particles = ParticleSystem()

        self.money = 250  # Меньше стартовых денег (было 300)
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

        self.top_ui = TopUIPanel()

    def on_draw(self):
        self.clear()

        if self.state == "menu":
            self.main_menu.draw()
            return

        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0

        arcade.get_window().ctx.viewport = (shake_x, shake_y, SCREEN_WIDTH, SCREEN_HEIGHT)

        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            for y in range(0, SCREEN_HEIGHT - 110, GRID_SIZE):
                wave = math.sin(self.frame * 0.08 + x * 0.02 + y * 0.02) * 5
                base_color = (32 + int(wave), 52 + int(wave), 32)
                draw_rectangle_filled(x + GRID_SIZE // 2, y + GRID_SIZE // 2,
                                      GRID_SIZE - 2, GRID_SIZE - 2, base_color)

        for i in range(len(PATH) - 1):
            arcade.draw_line(PATH[i][0], PATH[i][1], PATH[i + 1][0], PATH[i + 1][1],
                             (60, 50, 70), 44)
            arcade.draw_line(PATH[i][0], PATH[i][1], PATH[i + 1][0], PATH[i + 1][1],
                             (80, 70, 90), 38)
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

        for i in range(1, len(PATH) - 1):
            px, py = PATH[i]
            arcade.draw_circle_filled(px, py, 24, (50, 40, 60))
            arcade.draw_circle_filled(px, py, 22, (60, 50, 70))
            arcade.draw_circle_filled(px, py, 19, (80, 70, 90))
            arcade.draw_circle_outline(px, py, 15, (100, 90, 110), 2)
            arcade.draw_circle_filled(px, py, 4, (100, 90, 110))

        grid_x = (self.mouse_x // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
        grid_y = (self.mouse_y // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2

        if (self.mouse_y < SCREEN_HEIGHT - 110 and
                self.is_valid_tower_position(grid_x, grid_y)):
            pulse = abs(math.sin(self.frame * 0.1)) * 30 + 50
            draw_rectangle_filled(grid_x, grid_y, GRID_SIZE - 4, GRID_SIZE - 4,
                                  (80, 150, 80, int(pulse)))
            draw_rectangle_outline(grid_x, grid_y, GRID_SIZE - 4, GRID_SIZE - 4,
                                   PIXEL_COLORS['green'], 2)

        self.particles.draw()

        for tower in self.towers:
            tower.draw(selected=(tower == self.selected_tower))
            if tower == self.selected_tower:
                arcade.draw_circle_outline(tower.center_x, tower.center_y,
                                           tower.range, (*PIXEL_COLORS['white'], 80), 2)

        for enemy in self.enemies:
            enemy.draw()

        for bullet in self.bullets:
            bullet.draw()

        enemies_count = len([e for e in self.enemies if not e.dead])
        self.top_ui.draw(self.money, self.base_health, self.wave_manager.wave, enemies_count)

        if self.selected_tower:
            info_y = SCREEN_HEIGHT - 125
            draw_rectangle_filled(SCREEN_WIDTH // 2, info_y, 400, 25, (20, 20, 30, 200))
            info_text = f"LVL {self.selected_tower.level} | DMG: {self.selected_tower.damage} | UPGRADE: ${self.selected_tower.upgrade_cost}"
            arcade.draw_text(info_text, SCREEN_WIDTH // 2, info_y,
                             PIXEL_COLORS['yellow'], 12, anchor_x="center", anchor_y="center", bold=True)

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

        arcade.get_window().ctx.viewport = (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

    def draw_game_over(self):
        draw_rectangle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                              SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 200))

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

        can_start = not self.wave_manager.active and len(self.enemies) == 0
        self.top_ui.update(self.mouse_x, self.mouse_y, self.selected_tower_type, self.money, can_start)

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
                try:
                    sound = arcade.load_sound("death.wav")
                    arcade.play_sound(sound)
                except Exception:
                    pass
                self.enemies.remove(enemy)
            elif enemy.path_index >= len(PATH) - 1:
                self.base_health -= 1
                self.screen_shake = 10
                self.top_ui.trigger_health_flash()
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

        if y > SCREEN_HEIGHT - 110:
            clicked_type = self.top_ui.get_clicked_tower_type(x, y)
            if clicked_type:
                self.selected_tower_type = clicked_type
                return

            if self.top_ui.is_start_button_clicked(x, y):
                if not self.wave_manager.active and not self.enemies:
                    self.wave_manager.start_wave()
                    self.top_ui.start_button.click()
                    self.top_ui.trigger_wave_flash()
            return

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

        grid_x = (x // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
        grid_y = (y // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2

        if not self.is_valid_tower_position(grid_x, grid_y):
            return

        tower_costs = {"basic": 80, "sniper": 250, "slow": 180}
        cost = tower_costs[self.selected_tower_type]

        if self.money >= cost:
            tower = Tower(grid_x, grid_y, self.selected_tower_type)
            self.towers.append(tower)
            self.money -= cost
            self.particles.emit_explosion(grid_x, grid_y, PIXEL_COLORS['green'], 8)

    def is_valid_tower_position(self, x, y):
        for i in range(len(PATH) - 1):
            x1, y1 = PATH[i]
            x2, y2 = PATH[i + 1]

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