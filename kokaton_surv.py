import os
import sys
import pygame as pg
import pyautogui
import time
import math

WIDTH, HEIGHT = 800, 600 
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
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
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
            self.rect.centerx += dx * 5  # スピード調整
            self.rect.centery += dy * 5

class Enemy(pg.sprite.Sprite):
    """
    敵キャラクターに関するクラス
    """
    def __init__(self, xy: tuple[int, int]):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load("fig/10.png"), 0, 1.0)
        self.rect = self.image.get_rect(center=xy)
        self.speed = 2
        self.stop_distance = 500
        self.last_shot_time = 0
        self.shoot_interval = 400 # ミリ秒単位で発射間隔を設定

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
            dx = target_pos[0] - self.rect.centerx
            dy = target_pos[1] - self.rect.centery
            angle = math.atan2(dy, dx)
            bullet_dx = math.cos(angle)
            bullet_dy = math.sin(angle)
            bullet = Bullet(self.rect.center, (bullet_dx, bullet_dy))
            self.last_shot_time = current_time
            return bullet
        return None

class Bullet(pg.sprite.Sprite):
    """
    弾に関するクラス
    """
    def __init__(self, pos, direction):
        super().__init__()
        self.image = pg.Surface((10, 10))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.speed = 5
        self.direction = direction

    def update(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

def main():
    pg.display.set_caption("吸血鬼生存猪")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    font = pg.font.Font(None, 80)

    # 背景画像の読み込み
    background_image = pg.image.load('fig/pg_bg.jpg').convert()

    bird = Bird(1, (WIDTH // 2, HEIGHT // 2))  # 1はファイル名に対応
    enemy = Enemy((100, 100))

    all_sprites = pg.sprite.Group()
    all_sprites.add(bird)
    all_sprites.add(enemy)

    bullets = pg.sprite.Group()

    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return
        
        # マウスの現在位置を取得
        mouse_pos = pg.mouse.get_pos()
        # こうかとんの更新
        all_sprites.update(mouse_pos)
        enemy.update(bird.rect.center)

        # 現在の時間を取得
        current_time = pg.time.get_ticks()

        # 敵が一定距離に達したら弾を発射
        bullet = enemy.shoot(bird.rect.center, current_time)
        if bullet:
            bullets.add(bullet)

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
