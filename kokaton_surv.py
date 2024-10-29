import os
import sys
import pygame as pg
import pyautogui
import time
import math

WIDTH, HEIGHT = 1800, 1000 
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#以下に機能の追加

class Player(pg.sprite.Sprite):
    """
    主人公（こうかとん）の経験値やレベルを管理する為のクラス
    経験値を集めた時の処理を実行する
    引数num：画像の番号の指定
    """
    def __init__(self, num: int) -> None: 
        super().__init__()
        self.experience = 0
        self.level = 1
        self.experience_threshold = 100  # 1レベル上がるための経験値
        self.level_up_multiplier = 1.5  # レベルアップごとの閾値増加係数
        self.attack_cooldown = 500  # 攻撃間隔（ミリ秒）
        self.last_attack_time = pg.time.get_ticks()  # 最後の攻撃時間
        
        # こうかとん画像の設定
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        self.image = img0
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # 初期位置

    def collect_experience(self, orb) -> None:
        if orb:
            self.experience += orb.value
            print(f"経験値取得: {orb.value}ポイント")
            self.check_level_up()

    def check_level_up(self):
        while self.experience >= self.experience_threshold:
            self.experience -= self.experience_threshold
            self.level += 1
            print(f"レベルアップ! 現在のレベル: {self.level}")
            self.experience_threshold = int(self.experience_threshold * self.level_up_multiplier)
   
    def attack(self, enemy_group): # 攻撃を判定する関数
        current_time = pg.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_cooldown:
            self.last_attack_time = current_time
            # ここで一番近い敵を探す
            closest_enemy = None
            closest_distance = float("inf")
            # 弾を撃つ処理
            for enemy in enemy_group:
                distanceX = self.rect.centerx - enemy.rect.centerx
                distanceY = self.rect.centery - enemy.rect.centery
                total_distance = math.hypot(distanceX, distanceY)
                if total_distance < closest_distance:
                    closest_distance = total_distance
                    closest_enemy = enemy

             # 近い敵に攻撃
            if closest_enemy:
                # 弾を撃つ処理
                if closest_enemy.rect.colliderect(self.rect):  # ダメージを与えた場合:
                    closest_enemy.defeat()
                    return True
                
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
            (1,   0): img,  # 右
            (1,  -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0,  -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1,  0): img0,  # 左
            (-1,  1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0,   1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (1,   1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
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


class ExperienceOrb(pg.sprite.Sprite):
    """
    経験値に関するクラス
    """
    def __init__(self, value, position) -> None:
        super().__init__()
        self.value = value
        self.image = pg.Surface((20, 20))
        self.image.fill((255, 215, 0))  # 黄金色の経験値玉
        self.rect = self.image.get_rect(center=position)

class Enemy(pg.sprite.Sprite):
    """
    敵に関するクラス
    （他の人が敵のクラスを書くのでこれは仮置き）
    """
    def __init__(self, name, experience_value, position):
        super().__init__()
        self.name = name
        self.experience_value = experience_value
        self.image = pg.Surface((40, 40))
        self.image.fill((255, 0, 0))  # 赤色の敵
        self.rect = self.image.get_rect(center=position)
        self.health = 100 # 敵の体力

    def defeat(self):
        return ExperienceOrb(self.experience_value, self.rect.center)
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return True  # 敵が倒された
        return False
    
class Bullet_ko(pg.sprite.Sprite):
    """
    弾に関するクラス
    """
    def __init__(self, start_pos, direction) -> None:
        super().__init__()
        self.image = pg.Surface((10, 10))
        self.image.fill((0, 255, 0))  # 緑色の弾
        self.rect = self.image.get_rect(center=start_pos)
        self.direction = direction

    def update(self):
        self.rect.centerx += self.direction[0] * 10  # 弾の移動速度
        self.rect.centery += self.direction[1] * 10  # 弾の移動速度



#メイン関数-------------------------------------------------------------------------------------
def main():
    pg.display.set_caption("吸血鬼生存猪")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    font = pg.font.Font(None, 80)

    # 背景画像の読み込み
    background_image = pg.image.load('fig/pg_bg.jpg').convert()

    bird = Bird(1, (WIDTH // 2, HEIGHT // 2))  # 1はファイル名に対応
    player = Player(1)
    
    #複数敵の生成（他のメンバーが敵を作成しているので仮置き）
    enemy_group = pg.sprite.Group()
    for i in range(5):  # 敵を5体生成
        enemy = Enemy(f"Goblin{i+1}", 50, (WIDTH // 4 + i * 100, HEIGHT // 4))
        enemy_group.add(enemy)

    all_sprites = pg.sprite.Group()
    all_sprites.add(bird)
    all_sprites.add(enemy_group) # 複数の敵を追加する

    experience_orbs = pg.sprite.Group() # 経験値玉を格納するためのグループ
    bullets = pg.sprite.Group()  # 弾を格納するためのグループ

    last_attack_time = 0
    attack_interval = 500  # 攻撃間隔（ミリ秒）
    damage = 20  # 弾のダメージ
    
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        
        # 自動で攻撃する
        current_time = pg.time.get_ticks()
        if current_time - last_attack_time > attack_interval:
            # 弾の発射位置と方向を計算
            closest_enemy = None
            closest_distance = float('inf')
            for enemy in enemy_group:
                distance = math.hypot(bird.rect.centerx - enemy.rect.centerx, bird.rect.centery - enemy.rect.centery)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_enemy = enemy
            if closest_enemy:
                dir = (closest_enemy.rect.centerx - bird.rect.centerx, closest_enemy.rect.centery - bird.rect.centery)
                distance = math.hypot(*dir)
                if distance > 0:
                    dir = (dir[0] / distance, dir[1] / distance)
                    bul = Bullet_ko(bird.rect.center, dir)
                    all_sprites.add(bul)
                    bullets.add(bul)
                    last_attack_time = current_time
        
        # 弾の更新
        bullets.update()

        # 弾が敵に当たった場合の処理
        for bul in bullets:
            for enemy in enemy_group:
                if bul.rect.colliderect(enemy.rect):
                    if enemy.take_damage(damage):
                        orb = enemy.defeat()
                        if orb:
                            experience_orbs.add(orb)
                    bullets.remove(bul)
                    all_sprites.remove(bul)

        # マウスの現在位置を取得
        mouse_pos = pg.mouse.get_pos()
        # こうかとんの更新
        bird.update(mouse_pos)


        # 経験値玉を拾ったときの処理
        for orb in experience_orbs:
            if bird.rect.colliderect(orb.rect):
                player.collect_experience(orb)
                experience_orbs.remove(orb)
        
        # 画面の更新
        screen.fill((50, 50, 50))
        # 背景をループ表示
        for x in range(-WIDTH, WIDTH * 2, background_image.get_width()):
            screen.blit(background_image, (x, 0))
        
        all_sprites.draw(screen)
        experience_orbs.draw(screen)  # 経験値玉を描画

        txt = font.render(f"Level: {player.level}, Exp: {player.experience}", True, (255, 255, 255))
        screen.blit(txt, [300, 200])

        pg.display.update()
        tmr += 1        
        clock.tick(60)# FPS:60


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()