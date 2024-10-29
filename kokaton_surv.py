import os
import sys
import pygame as pg
import pyautogui
import time
import math
import random

WIDTH, HEIGHT = 1800, 1000 
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 1.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.image = self.imgs[(1, 0)] # 初期画像
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # 初期位置は画面中央に配置

    def update(self, mouse_pos):
        # マウスの方向に移動
        dx, dy = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance > 0:
            dx /= distance
            dy /= distance
            self.rect.centerx += dx * 7  # スピード調整
            self.rect.centery += dy * 7

class Enemy(pg.sprite.Sprite):
    """
    敵キャラクターに関するクラス
    """
    def __init__(self, num: int, xy: tuple[int, int], stop_distance: int, shoot_interval: int, bullet_speed: int, shoot_pattern: str, bullet_color: tuple, bullet_radius:int, speed:float):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 1.0)
        self.rect = self.image.get_rect(center=xy)
        self.speed = speed
        self.stop_distance = stop_distance
        self.last_shot_time = 0
        self.shoot_interval = shoot_interval  # ミリ秒単位で発射間隔を設定
        self.bullet_speed = bullet_speed  # 弾の速度を設定
        self.shoot_pattern = shoot_pattern  # 発射パターンを設定
        self.bullet_color = bullet_color  # 弾の色を設定
        self.bullet_radius = bullet_radius  #弾の半径を設定

    def update(self, target_pos):
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance > self.stop_distance:
            dx /= distance
            dy /= distance
            self.rect.centerx += dx * self.speed
            self.rect.centery += dy * self.speed

    def shoot(self, target_pos, current_time):
        if current_time - self.last_shot_time > self.shoot_interval:
            bullets = []
            if self.shoot_pattern == "spread":
                # 円形に弾を発射
                for angle in range(0, 360, 10):  # 45度間隔で発射
                    rad = math.radians(angle)
                    bullet_dx = math.cos(rad) * self.bullet_speed
                    bullet_dy = math.sin(rad) * self.bullet_speed
                    bullets.append(Bullet(self.rect.center, (bullet_dx, bullet_dy), self.bullet_color, self.bullet_radius))
            elif self.shoot_pattern == "direct":
                # ターゲットに直進
                dx = target_pos[0] - self.rect.centerx
                dy = target_pos[1] - self.rect.centery
                distance = math.hypot(dx, dy)
                if distance > 0:
                    dx /= distance
                    dy /= distance
                    bullet_dx = dx * self.bullet_speed
                    bullet_dy = dy * self.bullet_speed
                    bullets.append(Bullet(self.rect.center, (bullet_dx, bullet_dy), self.bullet_color, self.bullet_radius))
            elif self.shoot_pattern == "wave":
                # ターゲットの方向に波状に弾を発射
                dx = target_pos[0] - self.rect.centerx
                dy = target_pos[1] - self.rect.centery
                base_angle = math.degrees(math.atan2(dy, dx))
                for angle in range(-30, 31, 15):  # -30度から30度まで15度間隔で発射
                    rad = math.radians(base_angle + angle)
                    bullet_dx = math.cos(rad) * self.bullet_speed
                    bullet_dy = math.sin(rad) * self.bullet_speed
                    bullets.append(Bullet(self.rect.center, (bullet_dx, bullet_dy), self.bullet_color, self.bullet_radius))
            elif self.shoot_pattern == "random":
                # ランダム方向に弾を発射
                for _ in range(8):  # 8方向にランダム発射
                    angle = random.uniform(0, 360)
                    rad = math.radians(angle)
                    bullet_dx = math.cos(rad) * self.bullet_speed
                    bullet_dy = math.sin(rad) * self.bullet_speed
                    bullets.append(Bullet(self.rect.center, (bullet_dx, bullet_dy), self.bullet_color, self.bullet_radius))
            self.last_shot_time = current_time
            return bullets
        return []

class Bullet(pg.sprite.Sprite):
    """
    弾に関するクラス
    """
    def __init__(self, pos, direction, color, radius):
        super().__init__()
        self.image = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA)
        pg.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=pos)
        self.direction = direction

    def update(self):
        self.rect.x += self.direction[0]
        self.rect.y += self.direction[1]

def main():
    pg.display.set_caption("吸血鬼生存猪")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    font = pg.font.Font(None, 80)

    # 背景画像の読み込み
    background_image = pg.image.load('fig/pg_bg.jpg').convert()

    bird = Bird(1, (WIDTH // 2, HEIGHT // 2))  # 1はファイル名に対応

    # 敵の設定リスト
    enemy_settings = [
        {"num": 10, "xy": (100, 100), "stop_distance": 0, "shoot_interval": 1000, "bullet_speed": 5, "shoot_pattern": "spread", "bullet_color": (255, 0, 0), "bullet_radius":6, "speed":1.342},
        {"num": 11, "xy": (200, 100), "stop_distance": 0, "shoot_interval": 1200, "bullet_speed": 8, "shoot_pattern": "direct", "bullet_color": (75, 172, 0), "bullet_radius":7, "speed":1.000001},
        {"num": 12, "xy": (300, 100), "stop_distance": 0, "shoot_interval": 3600, "bullet_speed": 7, "shoot_pattern": "wave", "bullet_color": (0, 0, 255), "bullet_radius":8, "speed":1.059},
        {"num": 13, "xy": (400, 100), "stop_distance": 0, "shoot_interval": 2500, "bullet_speed": 8, "shoot_pattern": "random", "bullet_color": (255, 174, 0), "bullet_radius":6, "speed":2.0},
        {"num": 2, "xy": (200, 100), "stop_distance": 0, "shoot_interval": 1200, "bullet_speed": 8, "shoot_pattern": "direct", "bullet_color": (75, 172, 0), "bullet_radius":7, "speed":1.67},
        {"num": 3, "xy": (300, 100), "stop_distance": 0, "shoot_interval": 3600, "bullet_speed": 7, "shoot_pattern": "wave", "bullet_color": (0, 0, 255), "bullet_radius":8, "speed":2.3},
        {"num": 4, "xy": (400, 100), "stop_distance": 0, "shoot_interval": 2500, "bullet_speed": 8, "shoot_pattern": "random", "bullet_color": (255, 174, 0), "bullet_radius":6, "speed":1.22},
    ]

    enemies = [Enemy(**settings) for settings in enemy_settings]

    all_sprites = pg.sprite.Group()
    all_sprites.add(bird)
    all_sprites.add(*enemies)

    bullets = pg.sprite.Group()

    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return
        
        # マウスの現在位置を取得
        mouse_pos = pg.mouse.get_pos()
        # こうかとんの更新
        all_sprites.update(mouse_pos)
        for enemy in enemies:
            enemy.update(bird.rect.center)

            # 現在の時間を取得
            current_time = pg.time.get_ticks()

            # 敵が一定距離に達したら弾を発射
            new_bullets = enemy.shoot(bird.rect.center, current_time)
            bullets.add(*new_bullets)


        # 敵の数が3以下になったら補充
        if len(enemies) <= 7:
            new_enemy_settings = random.choice(enemy_settings)
            new_enemy = Enemy(**new_enemy_settings)
            enemies.append(new_enemy)
            all_sprites.add(new_enemy)

        # 弾の更新
        bullets.update()

        # 画面の更新
        screen.fill((50, 50, 50))
        # 背景をループ表示
        for x in range(-WIDTH, WIDTH * 2, background_image.get_width()):
            screen.blit(background_image, (x, 0))
        
        all_sprites.draw(screen)
        bullets.draw(screen)

        txt = font.render(str(tmr), True, (255, 255, 255))
        screen.blit(txt, [300, 200])

        pg.display.update()
        tmr += 1        
        clock.tick(60)# FPS:60


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
