import os
import sys
import pygame as pg
import pyautogui
import time
import math
import colorsys

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




def rainbow_color(index, max_index):
    """虹色のカラーを取得する関数"""
    hue = index / max_index
    r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(hue, 1.0, 1.0)]
    return (r, g, b)

def show_rules(screen: pg.Surface):
    # BGM
    pg.mixer.music.load("setumei.mp3")
    pg.mixer.music.set_volume(0.5)  # 音量を50%に設定
    pg.mixer.music.play(-1)  # ループ再生

    # フォントを読み込む
    font_path = "font/ipaexg.ttf"  # プロジェクトフォルダに配置したフォントファイル
    font = pg.font.Font(font_path, 30)  # フォントサイズ30で指定
    
    # ルールテキストを設定
    rules_texts = [
        "吸血鬼生存猪のルール説明",
        "1. マウスを使ってこうかとんを動かします。",
        "2. 敵に当たらないよう注意して、", 
        "経験値を獲得しましょう！！",
        "エンターキーを押してカウントダウンを開始します。"  # 最後のテキスト
    ]
    
    # こうかとん画像の読み込みと初期位置設定
    koukaton_img = pg.image.load("fig/2.png")
    koukaton_rect = koukaton_img.get_rect(midright=(WIDTH, HEIGHT // 2 - 100))  # 少し上に調整

    # エンターキーが押されるまでループ
    waiting = True
    clock = pg.time.Clock()  # フレームレート管理用のクロック
    blink_timer = 0  # 点滅用のタイマー
    timeout_start = pg.time.get_ticks()  # 開始時刻の取得

    while waiting:
        screen.fill((255, 180, 100))  

        # 各テキストを虹色で描画
        for i, text in enumerate(rules_texts[:-1]):  # 最後のテキスト以外を表示
            color = rainbow_color(i, len(rules_texts) - 1)
            render_text = font.render(text, True, color)
            text_rect = render_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 50))
            screen.blit(render_text, text_rect)

        # 点滅するテキストの処理
        blink_timer += 1
        if blink_timer % 60 < 30:  # 60フレームごとに15フレーム点灯
            last_text = rules_texts[-1]
            last_color = (255, 0, 0)  # 赤色
            render_last_text = font.render(last_text, True, last_color)
            last_text_rect = render_last_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + (len(rules_texts) - 1) * 50))
            screen.blit(render_last_text, last_text_rect)


        # こうかとん画像を右から左に高速で移動
        koukaton_rect.x -= 10  # 移動速度
        if koukaton_rect.right < 0:  # 左端に達したらリセットして右端に戻す
            koukaton_rect.left = WIDTH
        screen.blit(koukaton_img, koukaton_rect)

        # 一定時間待機で放置メッセージ
        elapsed_time = (pg.time.get_ticks() - timeout_start) / 1000
        if elapsed_time > 20:  
            pg.mixer.music.stop()  
            pg.mixer.music.load("dededon.mp3")  
            pg.mixer.music.play(-1)  

            screen.fill((0, 0, 0)) 

            large_font = pg.font.Font(font_path, 60)  

            alert_text = large_font.render("放置してるな！？", True, (255, 0, 0))
            alert_text_rect = alert_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(alert_text, alert_text_rect)
            pg.display.flip()
            pg.time.delay(5600)  

            pg.quit()
            sys.exit()


        pg.display.flip()  # 画面更新

        # イベント処理
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                pg.mixer.music.stop()  
                waiting = False

        clock.tick(60)  # フレームレートを60に制限




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


    # フォントパスの設定
    font_path = "font/ipaexg.ttf"  # 日本語フォントのパス
    font = pg.font.Font(font_path, 30)  # 日本語フォントを読み込み

    # ルール説明の表示
    show_rules(screen)  # ルール説明の呼び出し

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