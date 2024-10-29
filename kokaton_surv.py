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

def countdown(screen: pg.Surface, font: pg.font.Font):
    # カウントダウンのテキストと対応する画像を設定
    countdown_texts = ["3", "2", "1", "Start!"]
    countdown_images = [
        pg.image.load("fig/0.png"),  # 3の画像
        pg.image.load("fig/2.png"),  # 2の画像
        pg.image.load("fig/3.png"),  # 1の画像
        pg.image.load("fig/9.png")  # Startの画像
    ]

    for i, text in enumerate(countdown_texts):
        screen.fill((0, 0, 0))  # 背景を黒にしてリセット
        
        # テキストを描画
        render_text = font.render(text, True, (255, 255, 255))
        text_rect = render_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(render_text, text_rect)

        # 対応する画像を描画
        #image = pg.transform.scale(countdown_images[i], (200, 200))  # 画像のサイズを調整
        image = pg.transform.smoothscale(countdown_images[i], (200, 200))  # 画像のサイズを調整
        image_rect = image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))  # 画像の位置を調整
        screen.blit(image, image_rect)

        pg.display.flip()  # 画面更新
        time.sleep(0.5)  # 1秒待機

#メイン関数
def main():
    pg.display.set_caption("吸血鬼生存猪")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    font = pg.font.Font(None, 80)

    # 背景画像の読み込み
    background_image = pg.image.load('fig/pg_bg.jpg').convert()

    bird = Bird(1, (WIDTH // 2, HEIGHT // 2))  # 1はファイル名に対応

    all_sprites = pg.sprite.Group()
    all_sprites.add(bird)

    countdown_font = pg.font.Font(None, 120)
    countdown(screen, countdown_font)  # カウントダウンの呼び出し

    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return
        
        # マウスの現在位置を取得
        mouse_pos = pg.mouse.get_pos()
        # こうかとんの更新
        all_sprites.update(mouse_pos)
        # 画面の更新
        screen.fill((50, 50, 50))
        # 背景をループ表示
        for x in range(-WIDTH, WIDTH * 2, background_image.get_width()):
            screen.blit(background_image, (x, 0))
        
        all_sprites.draw(screen)

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