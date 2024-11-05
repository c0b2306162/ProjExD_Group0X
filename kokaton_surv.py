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


#背景を無限生成
class Haikei:
    """
    背景に関するクラス
    """
    def __init__(self, image_path):
        """
        背景画像の読み込み
        初期位置の設定
        """
        self.image = pg.image.load(image_path).convert()
        self.background_width, self.background_height = self.image.get_size()
        self.background_x = 0
        self.background_y = 0

    def update(self, bird_rect):
        # 背景の移動量を計算
        dx, dy = bird_rect.centerx - WIDTH // 2, bird_rect.centery - HEIGHT // 2
        self.background_x -= dx * 0.015  # 0.1は移動のスムーズさを調整する係数
        self.background_y -= dy * 0.015

    def draw(self, screen):
        # キャラクター周辺の背景を無限に繰り返し表示
        offset_x = self.background_x % self.background_width
        offset_y = self.background_y % self.background_height

        # 背景をタイル状に配置し、キャラクターの周囲に表示
        start_x = int(-self.background_width + offset_x)
        start_y = int(-self.background_height + offset_y)

        for x in range(start_x, WIDTH, self.background_width):
            for y in range(start_y, HEIGHT, self.background_height):
                screen.blit(self.image, (x, y))


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
