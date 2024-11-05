import os
import sys
import pygame as pg
import pyautogui
import time
import math

WIDTH, HEIGHT = 800, 600 
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#以下に機能の追加
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

    def update(self, mousu_pos):
        # マウスの方向に移動
        dx, dy = mousu_pos[0] - self.rect.centerx, mousu_pos[1] - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance > 0:
            dx /= distance
            dy /= distance
            self.rect.centerx += dx * 5  # スピード調整
            self.rect.centery += dy * 5

#背景の表示：連続画像を100×100で表示
class Haikei:
    """
    背景に関するクラス
    """
    def __init__(self, image_path):
        self.image = pg.image.load(image_path).convert()
        self.background_x = 0
        self.background_y = 0

    def update(self, bird_rect):
        # 背景の移動量を計算
        dx, dy = bird_rect.centerx - WIDTH // 2, bird_rect.centery - HEIGHT // 2
        distance = math.hypot(dx, dy)

        if distance > 0:
            dx /= distance
            dy /= distance
            move_speed = 5
            self.background_x -= dx * (move_speed / 5)  # 背景の移動を調整
            self.background_y -= dy * (move_speed / 5)  # 背景の移動を調整

        # 背景の移動に応じた制限
        if bird_rect.centerx < WIDTH * 0.45:
            self.background_x += 3  # 左端に近づいたら背景を右に
        elif bird_rect.centerx > WIDTH * 0.55:
            self.background_x -= 3  # 右端に近づいたら背景を左に

        if bird_rect.centery < HEIGHT * 0.45:
            self.background_y += 3  # 上端に近づいたら背景を下に
        elif bird_rect.centery > HEIGHT * 0.55:
            self.background_y -= 3  # 下端に近づいたら背景を上に

    def draw(self, screen):
        # 背景のループ表示
        for x in range(-100, 100):
            for y in range(-100, 100):
                screen.blit(self.image, (x * 1000 + self.background_x, y * 1000 + self.background_y))

#メイン関数
def main():
    pg.display.set_caption("吸血鬼生存猪")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    font = pg.font.Font(None, 80)

    # 背景クラスのインスタンスを作成
    haikei = Haikei('fig/haikei.jpg')

    bird = Bird(1, (WIDTH // 2, HEIGHT // 2))  # 1はファイル名に対応

    all_sprites = pg.sprite.Group()
    all_sprites.add(bird)

    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        
        # マウスの現在位置を取得
        mouse_pos = pg.mouse.get_pos()
        # こうかとんの更新
        bird.update(mouse_pos)
        haikei.update(bird.rect)

        # 画面の更新
        screen.fill((50, 50, 50))
        haikei.draw(screen)
        all_sprites.draw(screen)

        txt = font.render(str(tmr), True, (255, 255, 255))
        screen.blit(txt, [300, 200])

        pg.display.update()
        tmr += 1        
        clock.tick(60)  # FPS:60


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
