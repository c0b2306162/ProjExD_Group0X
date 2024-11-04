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
        self.image = self.imgs[(1, 0)]  # 初期画像
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # 初期位置は画面中央に配置
        self.hp = 100  # HP残量
        self.xp = 0  # 獲得XP

    def update(self, mouse_pos, bullets):
        # マウスの方向に移動
        dx, dy = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance > 0:
            dx /= distance
            dy /= distance
            self.rect.centerx += dx * 7  # スピード調整
            self.rect.centery += dy * 7

        # Check for collisions with bullets
        collided_bullet = pg.sprite.spritecollideany(self, bullets)
        if collided_bullet:
            self.hp -= 7  # HPを7減らす
            collided_bullet.kill() # 一回あたったら弾は消滅
        if self.hp <= 0:
            self.hp = 0  # HPが0以下になっても0に留める
            return "gameover"  # gameover表示
        return "playing"  # クリックでリスタート
    
    def get_xp(self, amount):
        self.xp += amount
        if self.xp >= 100:
            self.xp -= 100
            self.hp = 100
            


class Enemy(pg.sprite.Sprite):
    """
    敵キャラクターに関するクラス
    """
    def __init__(self, num: int, xy: tuple[int, int], stop_distance: int, shoot_interval: int, bullet_speed: int, shoot_pattern: str, bullet_color: tuple, bullet_radius:int, speed:float, en_hp:int):
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
        self.en_hp = en_hp  #Hpを設定

    def update(self, target_pos):
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance > self.stop_distance:
            dx /= distance
            dy /= distance
            self.rect.centerx += dx * self.speed
            self.rect.centery += dy * self.speed
    
    def reduce_hp(self, amount):
        self.en_hp -= amount
        if self.en_hp <= 0:
            self.kill()
            return True
        return False

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

import pygame as pg

class Xp():
    def __init__(self):
        self.font = pg.font.Font(None, 80)  # Use a custom game-like font
        self.color = (255, 255, 255)
        self.value = 0
        self.image = self.font.render(f"xp: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (240, 10)  # Set position to the top-left corner

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"xp: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)


def main():
    pg.display.set_caption("吸血鬼生存猪")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    font = pg.font.Font(None, 80)
    xp = Xp()
    

    # 背景画像の読み込み
    #background_image = pg.image.load('fig/pg_bg.jpg').convert()

    bird = Bird(1, (WIDTH // 2, HEIGHT // 2))  # 1はファイル名に対応

    # 敵の設定リスト
    base_enemy_settings = [
        {"num": 10, "stop_distance": 0, "shoot_interval": 7000, "bullet_speed": 5, "shoot_pattern": "spread", "bullet_color": (255, 0, 0), "bullet_radius": 6, "speed": 1.342, "en_hp":200},
        {"num": 11, "stop_distance": 0, "shoot_interval": 6700, "bullet_speed": 8, "shoot_pattern": "direct", "bullet_color": (75, 172, 0), "bullet_radius": 7, "speed": 1.000001, "en_hp":80},
        {"num": 12, "stop_distance": 0, "shoot_interval": 9500, "bullet_speed": 7, "shoot_pattern": "wave", "bullet_color": (0, 0, 255), "bullet_radius": 8, "speed": 1.059, "en_hp":130},
        {"num": 13, "stop_distance": 0, "shoot_interval": 7900, "bullet_speed": 8, "shoot_pattern": "random", "bullet_color": (255, 174, 0), "bullet_radius": 6, "speed": 2.0, "en_hp":170},
        {"num": 11, "stop_distance": 0, "shoot_interval": 6200, "bullet_speed": 8, "shoot_pattern": "direct", "bullet_color": (75, 172, 0), "bullet_radius": 7, "speed": 1.67, "en_hp":80},
        {"num": 12, "stop_distance": 0, "shoot_interval": 5400, "bullet_speed": 7, "shoot_pattern": "wave", "bullet_color": (0, 0, 255), "bullet_radius": 8, "speed": 2.3, "en_hp":130},
        {"num": 13, "stop_distance": 0, "shoot_interval": 8700, "bullet_speed": 8, "shoot_pattern": "random", "bullet_color": (255, 174, 0), "bullet_radius": 6, "speed": 1.22, "en_hp":170},
    ]

    enemies = []
    for i in range(20):  # Generate 20 enemies
        settings = random.choice(base_enemy_settings).copy()
        settings["xy"] = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
        enemies.append(Enemy(**settings))

    all_sprites = pg.sprite.Group()
    all_sprites.add(bird)
    all_sprites.add(*enemies)

    bullets = pg.sprite.Group()

    tmr = 0
    game_state = "playing"  # Track the game state

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.MOUSEBUTTONDOWN:
                if game_state == "gameover":
                    mouse_pos = event.pos
                    if restart_button.collidepoint(mouse_pos):
                        main()  # Restart the game
                    elif quit_button.collidepoint(mouse_pos):
                        return  # Quit the game
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    if enemies:
                        enemy = enemies[0]
                        if enemy.reduce_hp(10):
                            enemies.remove(enemy)
                            bird.get_xp(50)
                            xp.value += 50
                    

        if game_state == "playing":
            # マウスの現在位置を取得
            mouse_pos = pg.mouse.get_pos()
            # こうかとんの更新
            game_state = bird.update(mouse_pos, bullets)  # Update bird and check game state
            for enemy in enemies:
                enemy.update(bird.rect.center)

                # 現在の時間を取得
                current_time = pg.time.get_ticks()

                # 敵が一定距離に達したら弾を発射
                new_bullets = enemy.shoot(bird.rect.center, current_time)
                bullets.add(*new_bullets)

            # 弾の更新
            bullets.update()

            # 画面の更新
            screen.fill((50, 50, 50))
            # 背景をループ表示
            # for x in range(-WIDTH, WIDTH * 2, background_image.get_width()):
            #     screen.blit(background_image, (x, 0))
            
            all_sprites.draw(screen)
            bullets.draw(screen)

            #  HP
            hp_text = font.render(f"HP: {bird.hp}", True, (255, 255, 255))
            screen.blit(hp_text, (10, 10))

            txt = font.render(str(tmr), True, (255, 255, 255))
            screen.blit(txt, [300, 200])

        elif game_state == "gameover":
            # game over 画面
            gameover_text = font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(gameover_text, (WIDTH // 2 - 200, HEIGHT // 2 - 40))

            restart_text = font.render("Restart", True, (255, 255, 255))
            quit_text = font.render("Quit", True, (255, 255, 255))

            # 各ボタン設置
            restart_button = pg.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 40, 200, 50)
            quit_button = pg.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)

            # ボタン描画
            pg.draw.rect(screen, (0, 255, 0), restart_button)
            pg.draw.rect(screen, (255, 0, 0), quit_button)

            # テキストをボタン中央に描画する
            restart_text_rect = restart_text.get_rect(center=restart_button.center)
            quit_text_rect = quit_text.get_rect(center=quit_button.center)

            screen.blit(restart_text, restart_text_rect.topleft)
            screen.blit(quit_text, quit_text_rect.topleft)


        xp.update(screen)
        pg.display.update()
        tmr += 1        
        clock.tick(60)  # FPS:60




if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
