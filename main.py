import arcade
import math
import random

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Tower Defense"

GRID_SIZE = 60
PATH_COLOR = (100, 100, 100)
GRID_COLOR = (60, 80, 60)
VALID_CELL_COLOR = (80, 120, 80, 100)

PATH = [
    (0, 400), (300, 400), (300, 200), (600, 200),
    (600, 500), (900, 500), (900, 300), (1200, 300)
]


class Bullet(arcade.Sprite):
    def __init__(self, x, y, target, damage, speed=8):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.target = target
        self.damage = damage
        self.speed = speed
        self.color = arcade.color.YELLOW
        self.width = 8
        self.height = 8

    def update(self, delta_time=0):
        if not self.target or self.target.health <= 0:
            self.remove_from_sprite_lists()
            return

        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < 10:
            self.target.health -= self.damage
            self.remove_from_sprite_lists()
            return

        self.center_x += (dx / distance) * self.speed
        self.center_y += (dy / distance) * self.speed

    def draw(self):
        arcade.draw_circle_filled(self.center_x, self.center_y, 4, self.color)


class Enemy(arcade.Sprite):
    def __init__(self, path, enemy_type="normal"):
        super().__init__()
        self.path = path
        self.path_index = 0
        self.center_x = path[0][0]
        self.center_y = path[0][1]

        self.enemy_type = enemy_type
        if enemy_type == "fast":
            self.max_health = 50
            self.speed = 2.5
            self.color = arcade.color.CYAN
            self.reward = 15
            self.width = 20
            self.height = 20
        elif enemy_type == "tank":
            self.max_health = 200
            self.speed = 0.8
            self.color = arcade.color.DARK_RED
            self.reward = 40
            self.width = 35
            self.height = 35
        else:
            self.max_health = 100
            self.speed = 1.5
            self.color = arcade.color.RED
            self.reward = 25
            self.width = 25
            self.height = 25

        self.health = self.max_health
        self.slow_factor = 1.0

    def update(self, delta_time=0):
        if self.path_index >= len(self.path) - 1:
            return

        target_x, target_y = self.path[self.path_index + 1]
        dx = target_x - self.center_x
        dy = target_y - self.center_y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < 5:
            self.path_index += 1
            if self.path_index >= len(self.path) - 1:
                return
        else:
            move_speed = self.speed * self.slow_factor
            self.center_x += (dx / distance) * move_speed
            self.center_y += (dy / distance) * move_speed

        self.slow_factor = min(1.0, self.slow_factor + 0.05)

    def draw(self):
        arcade.draw_circle_filled(self.center_x, self.center_y, self.width / 2, self.color)

        health_percent = self.health / self.max_health
        bar_width = self.width
        bar_height = 4
        arcade.draw_lbwh_rectangle_filled(
            self.center_x - bar_width / 2, self.center_y + self.height / 2 + 8 - bar_height / 2,
            bar_width, bar_height, arcade.color.BLACK
        )
        arcade.draw_lbwh_rectangle_filled(
            self.center_x - bar_width / 2, self.center_y + self.height / 2 + 8 - bar_height / 2,
            bar_width * health_percent, bar_height,
            arcade.color.GREEN
        )


class Tower(arcade.Sprite):
    def __init__(self, x, y, tower_type="basic"):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.tower_type = tower_type
        self.level = 1

        if tower_type == "sniper":
            self.range = 250
            self.damage = 80
            self.fire_rate = 90
            self.color = arcade.color.BLUE
            self.cost = 200
            self.upgrade_cost = 150
        elif tower_type == "slow":
            self.range = 150
            self.damage = 10
            self.fire_rate = 30
            self.color = arcade.color.LIGHT_BLUE
            self.cost = 150
            self.upgrade_cost = 100
            self.slow_effect = 0.5
        else:
            self.range = 180
            self.damage = 40
            self.fire_rate = 45
            self.color = arcade.color.DARK_GREEN
            self.cost = 100
            self.upgrade_cost = 80

        self.width = 40
        self.height = 40
        self.fire_cooldown = 0
        self.target = None

    def update(self, enemies):
        self.fire_cooldown = max(0, self.fire_cooldown - 1)

        if self.target and (self.target.health <= 0 or
                            self.get_distance(self.target) > self.range):
            self.target = None

        if not self.target:
            for enemy in enemies:
                if self.get_distance(enemy) <= self.range:
                    self.target = enemy
                    break

    def get_distance(self, enemy):
        return math.sqrt((self.center_x - enemy.center_x) ** 2 +
                         (self.center_y - enemy.center_y) ** 2)

    def can_fire(self):
        return self.fire_cooldown == 0 and self.target and self.target.health > 0

    def fire(self):
        self.fire_cooldown = self.fire_rate
        if self.tower_type == "slow" and self.target:
            self.target.slow_factor = self.slow_effect
        return Bullet(self.center_x, self.center_y, self.target, self.damage)

    def upgrade(self):
        self.level += 1
        self.damage = int(self.damage * 1.5)
        self.range = int(self.range * 1.1)
        self.fire_rate = int(self.fire_rate * 0.9)
        self.upgrade_cost = int(self.upgrade_cost * 1.5)

    def draw(self):
        arcade.draw_circle_filled(self.center_x, self.center_y, self.width / 2, self.color)
        arcade.draw_circle_outline(self.center_x, self.center_y, self.width / 2 + 2,
                                   arcade.color.WHITE, 2)

        if self.level > 1:
            arcade.draw_text(str(self.level), self.center_x - 5, self.center_y - 8,
                             arcade.color.WHITE, 14, bold=True)


class WaveManager:
    def __init__(self):
        self.wave = 0
        self.active = False
        self.spawn_timer = 0
        self.spawn_interval = 60
        self.enemies_to_spawn = []

    def start_wave(self):
        self.wave += 1
        self.active = True
        self.spawn_timer = 0

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


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_OLIVE_GREEN)

        self.towers = []
        self.enemies = arcade.SpriteList()
        self.bullets = arcade.SpriteList()

        self.money = 300
        self.base_health = 20
        self.selected_tower_type = "basic"
        self.selected_tower = None

        self.wave_manager = WaveManager()
        self.game_over = False
        self.paused = False

        self.mouse_x = 0
        self.mouse_y = 0

    def on_draw(self):
        self.clear()

        for i in range(len(PATH) - 1):
            arcade.draw_line(PATH[i][0], PATH[i][1], PATH[i + 1][0], PATH[i + 1][1],
                             PATH_COLOR, 40)

        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            for y in range(0, SCREEN_HEIGHT - 100, GRID_SIZE):
                if self.is_valid_tower_position(x + GRID_SIZE // 2, y + GRID_SIZE // 2):
                    arcade.draw_lrbt_rectangle_outline(x, x + GRID_SIZE, y, y + GRID_SIZE,
                                                       GRID_COLOR, 1)

        grid_x = (self.mouse_x // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
        grid_y = (self.mouse_y // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2

        if (self.mouse_y < SCREEN_HEIGHT - 100 and
                self.is_valid_tower_position(grid_x, grid_y)):
            arcade.draw_lbwh_rectangle_filled(grid_x - (GRID_SIZE - 4) // 2, grid_y - (GRID_SIZE - 4) // 2,
                                              GRID_SIZE - 4, GRID_SIZE - 4,
                                              VALID_CELL_COLOR)

        for tower in self.towers:
            tower.draw()
            if tower == self.selected_tower:
                arcade.draw_circle_outline(tower.center_x, tower.center_y,
                                           tower.range, arcade.color.WHITE, 2)

        for enemy in self.enemies:
            enemy.draw()

        for bullet in self.bullets:
            bullet.draw()

        arcade.draw_lbwh_rectangle_filled(0, SCREEN_HEIGHT - 100,
                                     SCREEN_WIDTH, 100, arcade.color.DARK_GRAY)

        arcade.draw_text(f"💰 ${self.money}", 20, SCREEN_HEIGHT - 70,
                         arcade.color.GOLD, 20, bold=True)
        arcade.draw_text(f"❤️ {self.base_health}", 200, SCREEN_HEIGHT - 70,
                         arcade.color.RED, 20, bold=True)
        arcade.draw_text(f"🌊 Wave {self.wave_manager.wave}", 360, SCREEN_HEIGHT - 70,
                         arcade.color.LIGHT_BLUE, 20, bold=True)

        tower_types = [
            ("Basic ($100)", "basic", 600),
            ("Sniper ($200)", "sniper", 800),
            ("Slow ($150)", "slow", 1000)
        ]

        for label, ttype, x in tower_types:
            color = arcade.color.GREEN if self.selected_tower_type == ttype else arcade.color.WHITE
            arcade.draw_text(label, x, SCREEN_HEIGHT - 70, color, 16, bold=True)

        if not self.wave_manager.active and not self.enemies:
            arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 80,
                                         200, 60, arcade.color.GREEN)
            arcade.draw_text("START WAVE", SCREEN_WIDTH - 220, SCREEN_HEIGHT - 60,
                             arcade.color.WHITE, 18, bold=True)

        if self.selected_tower:
            arcade.draw_text(f"Upgrade: ${self.selected_tower.upgrade_cost}",
                             SCREEN_WIDTH - 250, SCREEN_HEIGHT - 30,
                             arcade.color.YELLOW, 14)

        if self.game_over:
            arcade.draw_lbwh_rectangle_filled(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100,
                                         400, 200, arcade.color.BLACK)
            arcade.draw_text("GAME OVER", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2,
                             arcade.color.RED, 40, bold=True)

        if self.paused and not self.game_over:
            arcade.draw_text("PAUSED", SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2,
                             arcade.color.WHITE, 40, bold=True)

    def on_update(self, delta_time):
        if self.game_over or self.paused:
            return

        new_enemy = self.wave_manager.update()
        if new_enemy:
            self.enemies.append(new_enemy)

        self.enemies.update(delta_time)

        for enemy in list(self.enemies):
            if enemy.health <= 0:
                self.money += enemy.reward
                self.enemies.remove(enemy)
            elif enemy.path_index >= len(PATH) - 1:
                self.base_health -= 1
                self.enemies.remove(enemy)
                if self.base_health <= 0:
                    self.game_over = True

        for tower in self.towers:
            tower.update(self.enemies)
            if tower.can_fire():
                self.bullets.append(tower.fire())

        self.bullets.update(delta_time)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_over:
            return

        if y > SCREEN_HEIGHT - 100:
            if 600 <= x <= 750:
                self.selected_tower_type = "basic"
            elif 800 <= x <= 950:
                self.selected_tower_type = "sniper"
            elif 1000 <= x <= 1150:
                self.selected_tower_type = "slow"
            elif SCREEN_WIDTH - 250 <= x <= SCREEN_WIDTH - 50:
                if not self.wave_manager.active:
                    self.wave_manager.start_wave()
            return

        for tower in self.towers:
            if (abs(tower.center_x - x) < tower.width / 2 and
                    abs(tower.center_y - y) < tower.height / 2):
                if self.selected_tower == tower:
                    if self.money >= tower.upgrade_cost:
                        self.money -= tower.upgrade_cost
                        tower.upgrade()
                else:
                    self.selected_tower = tower
                return

        self.selected_tower = None

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

    def is_valid_tower_position(self, x, y):
        for px, py in PATH:
            if abs(x - px) < 60 and abs(y - py) < 60:
                return False
        for tower in self.towers:
            if abs(tower.center_x - x) < 30 and abs(tower.center_y - y) < 30:
                return False
        return True

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.paused = not self.paused


def main():
    window = GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()