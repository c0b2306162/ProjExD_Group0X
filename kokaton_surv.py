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

def show_rules(screen: pg.Surface):
    # フォントを読み込む
    font_path = "font/ipaexg.ttf"  # プロジェクトフォルダに配置したフォントファイル
    font = pg.font.Font(font_path, 30)  # フォントサイズ30で指定
    
    # ルールテキストを設定
    rules_texts = [
        "吸血鬼生存猪のルール説明",
        "1. マウスを使ってこうかとんを動かします。",
        "2. 敵に当たらないよう注意して、","得点を獲得しレベルアップしましょう！！",
        "エンターキーを押してカウントダウンを開始します。"
    ]
    
    # こうかとん画像の読み込みと初期位置設定
    koukaton_img = pg.image.load("fig/2.png")
    koukaton_rect = koukaton_img.get_rect(midright=(WIDTH, HEIGHT // 2 - 70))

    # エンターキーが押されるまでループ
    waiting = True
    clock = pg.time.Clock()  # フレームレート管理用のクロック
    blink_timer = 0  # 点滅用のタイマー

    while waiting:
        screen.fill((0, 0, 0))  # 背景を黒で塗りつぶし

        # 各テキストを描画
        for i, text in enumerate(rules_texts[:-1]):  # 最後のテキスト以外を表示
            render_text = font.render(text, True, (255, 255, 255))
            text_rect = render_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 50))
            screen.blit(render_text, text_rect)

        # 「エンターキーを押して…」のテキストを点滅させながら表示
        blink_timer += 1
        if blink_timer % 60 < 15:  # 点滅の速度を遅くする
            last_text = font.render(rules_texts[-1], True, (255, 0, 0))
            last_text_rect = last_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 200))
            screen.blit(last_text, last_text_rect)

        # こうかとん画像を右から左に高速で移動
        koukaton_rect.x -= 10
        if koukaton_rect.right < 0:  # 左端に達したらリセットして右端に戻す
            koukaton_rect.left = WIDTH
        screen.blit(koukaton_img, koukaton_rect)

        pg.display.flip()  # 画面更新

        # イベント処理
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                waiting = False

        clock.tick(60)  # フレームレートを60に制限


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

    show_rules(screen)  # ルール説明の呼び出し

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