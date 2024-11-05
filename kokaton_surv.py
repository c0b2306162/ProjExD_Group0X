import os
import sys
import pygame as pg
import random
import math

# ゲームの初期設定
WIDTH, HEIGHT = 1200, 600
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ゲームキャラクター（主人公、敵、弾、経験値）に関するクラス
class Bird(pg.sprite.Sprite):
    def __init__(self, num: int, xy: tuple[int, int]) -> None:
        """
        引数１ num:こうかとん画像ファイル名の番号
        引数２ xy:こうかとん画像の位置座標タプル
        """
        super().__init__()
        img = pg.image.load(f"fig/{num}.png")
        img0 = pg.transform.flip(img, True, False)
        self.original_image = pg.transform.scale(img, (60, 60))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=xy)
        self.speed = 5
        self.xp = 0
        self.hp = 100  # 主人公のHP

        self.imgs = {
            (1,   0): img0,  # 右
            (1,  -1): pg.transform.rotozoom(img0, 45, 1.0),  # 右上
            (0,  -1): pg.transform.rotozoom(img0, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img, -45, 1.0),  # 左上
            (-1,  0): img,  # 左
            (-1,  1): pg.transform.rotozoom(img, 45, 1.0),  # 左下
            (0,   1): pg.transform.rotozoom(img0, -90, 1.0),  # 下
            (1,   1): pg.transform.rotozoom(img0, -45, 1.0),  # 右下
        }

        self.image = self.imgs[(1, 0)]  # 初期画像
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # 初期位置は画面中央に配置
        
    def update(self, mouse_pos, en_bullets):
        # マウスの方向に移動
        dx, dy = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery

        distance = math.hypot(dx, dy)
        if distance > 0:
            dx /= distance
            dy /= distance
            self.rect.centerx += dx * 7  # スピード調整
            self.rect.centery += dy * 7

        angle = math.degrees(math.atan2(-dy, dx))  # Y軸反転 → 角度計算

        if -22.5 <= angle < 22.5:
            direction = (1, 0)          # 右
        elif 22.5 <= angle < 67.5:
            direction = (1, -1)         # 右上
        elif 67.5 <= angle < 112.5:
            direction = (0, -1)         # 上
        elif 112.5 <= angle < 157.5:
            direction = (-1, -1)        # 左上
        elif 157.5 <= angle or angle < -157.5:
            direction = (-1, 0)         # 左
        elif -157.5 <= angle < -112.5:
            direction = (-1, 1)         # 左下
        elif -112.5 <= angle < -67.5:
            direction = (0, 1)          # 下
        elif -67.5 <= angle < -22.5:
            direction = (1, 1)          # 右下   

        self.image = self.imgs[direction]
        self.rect = self.image.get_rect(center=self.rect.center)  # 画像の中心座標を維持

            # 弾との衝突判定
        collided_bullet = pg.sprite.spritecollideany(self, en_bullets)
        if collided_bullet:
            self.hp -= 7  # HPを7減らす
            collided_bullet.kill()  # 一回あたったら弾は消滅
        if self.hp <= 0:
            self.hp = 0  # HPが0以下になっても0に留める
            return "gameover"  # gameover表示
        return "playing"  # クリックでリスタート
 
    def take_damage(self):
        # 敵と接近した時にダメージを受ける処理
        self.hp -= 1
        print(f"hp:{self.hp}")
        if self.hp <= 0:
            print("Game Over")
            self.kill()
    
    def recover_hp(self):
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
    
    def hit(self):
        self.en_hp -= 1
        if self.en_hp <= 0:
            self.kill()
            return ExpOrb(self.rect.center)
        return None

    def shoot(self, target_pos, current_time, en_bullets):
        if current_time - self.last_shot_time > self.shoot_interval:
            if self.shoot_pattern == "spread":
                # 円形に弾を発射
                for angle in range(0, 360, 10):  # 45度間隔で発射
                    rad = math.radians(angle)
                    bullet_dx = math.cos(rad) * self.bullet_speed
                    bullet_dy = math.sin(rad) * self.bullet_speed
                    en_bullets.add(En_Bullet(self.rect.center, (bullet_dx, bullet_dy), self.bullet_color, self.bullet_radius))
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
                    en_bullets.add(En_Bullet(self.rect.center, (bullet_dx, bullet_dy), self.bullet_color, self.bullet_radius))
            elif self.shoot_pattern == "wave":
                # ターゲットの方向に波状に弾を発射
                dx = target_pos[0] - self.rect.centerx
                dy = target_pos[1] - self.rect.centery
                base_angle = math.degrees(math.atan2(dy, dx))
                for angle in range(-30, 31, 15):  # -30度から30度まで15度間隔で発射
                    rad = math.radians(base_angle + angle)
                    bullet_dx = math.cos(rad) * self.bullet_speed
                    bullet_dy = math.sin(rad) * self.bullet_speed
                    en_bullets.add(En_Bullet(self.rect.center, (bullet_dx, bullet_dy), self.bullet_color, self.bullet_radius))
            elif self.shoot_pattern == "random":
                # ランダム方向に弾を発射
                for _ in range(8):  # 8方向にランダム発射
                    angle = random.uniform(0, 360)
                    rad = math.radians(angle)
                    bullet_dx = math.cos(rad) * self.bullet_speed
                    bullet_dy = math.sin(rad) * self.bullet_speed
                    en_bullets.add(En_Bullet(self.rect.center, (bullet_dx, bullet_dy), self.bullet_color, self.bullet_radius))
            print(f"Shot {len(en_bullets)} bullets")
            self.last_shot_time = current_time
            return en_bullets
        return []

class En_Bullet(pg.sprite.Sprite):
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
        if not (0 <= self.rect.x <= WIDTH and 0 <= self.rect.y <= HEIGHT):
            self.kill()

# こうかとんの攻撃方法を管理するクラス
class Bullet(pg.sprite.Sprite):
    def __init__(self, pos, target_pos) -> None:
        super().__init__()
        self.image = pg.Surface((10, 10), pg.SRCALPHA) 
        pg.draw.circle(self.image, (0, 255, 255), (5, 5), 5)
        self.rect = self.image.get_rect(center=pos)  # 弾の初期位置を設定

        # ターゲットへの距離の計算
        dx, dy = target_pos[0] - pos[0], target_pos[1] - pos[1]
        distance = math.hypot(dx, dy)  # ターゲットまでの直線距離

        if distance > 0:  # distanceが0でない場合のみ速度ベクトルを計算
            self.speed = 10
            self.velocity = (dx / distance * self.speed, dy / distance * self.speed)
        else:
            self.velocity = (0, 0)  # distanceが0の場合は移動しない

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # 画面外に出た弾を削除
        if not (0 <= self.rect.x <= WIDTH and 0 <= self.rect.y <= HEIGHT):
            self.kill()  # spriteグループから削除

# 敵が落とす経験値の玉を管理するクラス
class ExpOrb(pg.sprite.Sprite):
    def __init__(self, pos) -> int:
        """
        経験値に関するクラス
        引数１ pos:経験値玉の落下する座標
        """
        super().__init__()
        self.image = pg.Surface((15, 15), pg.SRCALPHA)
        pg.draw.circle(self.image, (0, 255, 0), (7, 7), 7)
        self.rect = self.image.get_rect(center=pos)
        self.value = 10

#敵の再出現を管理するクラス
# class EnemyManager:
#     def __init__(self, all_sprites, enemies, respawn_time=300) -> None:
#         self.all_sprites = all_sprites
#         self.enemies = enemies
#         self.respawn_time = respawn_time #　復活するまでのフレーム数
#         self.respawn_timer = []

#     def update(self):
#         #敵の再出現を管理
#         for idx, timer in enumerate(self.respawn_timer):
#             self.respawn_timer[idx] -= 1
#             if self.respawn_timer[idx] <= 0:
#                 self.respawn_timer.pop(idx)
#                 self.spawn_enemy()
#         #敵の数を5～7体に保つ
#         if len(self.enemies) < 5:
#             self.spawn_enemy()

    # def spawn_enemy(self):
    #     enemy = Enemy((random.randint(0, WIDTH), random.randint(0, HEIGHT)))
    #     self.enemies.add(enemy)
    #     self.all_sprites.add(enemy)

    # def schedule_respawn(self):
    #     if len(self.enemies) < 7:
    #         self.respawn_timer.append(self.respawn_time)

class Xp():
    def __init__(self, value =0):
        self.font = pg.font.Font(None, 80)  # Use a custom game-like font
        self.color = (255, 255, 255)
        self.value = value
        self.image = self.font.render(f"xp: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (240, 10)  # Set position to the top-left corner

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"xp: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)

# ゲームのメインループ
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
    xp = Xp()
    font = pg.font.Font(None, 80)

    # プレイヤーと敵の初期化
    bird = Bird(3, (WIDTH // 2, HEIGHT // 2))
    bullets = pg.sprite.Group()
    # 背景クラスのインスタンスを作成
    haikei = Haikei('fig/haikei.jpg')

    
    # 背景画像の読み込み
    #background_image = pg.image.load('fig/pg_bg.jpg').convert()


    bullet_timer = 0


    # 敵の設定リスト
    base_enemy_settings = [
    {"num": 10, "xy": (random.randint(0, WIDTH), random.randint(0, HEIGHT)), "stop_distance": 0, "shoot_interval": 7000, "bullet_speed": 5, "shoot_pattern": "spread", "bullet_color": (255, 0, 0), "bullet_radius": 6, "speed": 1.342, "en_hp": 90},
    {"num": 11, "xy": (random.randint(0, WIDTH), random.randint(0, HEIGHT)), "stop_distance": 0, "shoot_interval": 6700, "bullet_speed": 8, "shoot_pattern": "direct", "bullet_color": (75, 172, 0), "bullet_radius": 7, "speed": 1.000001, "en_hp": 100},
    {"num": 12, "xy": (random.randint(0, WIDTH), random.randint(0, HEIGHT)), "stop_distance": 0, "shoot_interval": 9500, "bullet_speed": 7, "shoot_pattern": "wave", "bullet_color": (0, 0, 255), "bullet_radius": 8, "speed": 1.059, "en_hp": 200},
    {"num": 13, "xy": (random.randint(0, WIDTH), random.randint(0, HEIGHT)), "stop_distance": 0, "shoot_interval": 7900, "bullet_speed": 8, "shoot_pattern": "random", "bullet_color": (255, 174, 0), "bullet_radius": 6, "speed": 2.0, "en_hp": 150},
    {"num": 11, "xy": (random.randint(0, WIDTH), random.randint(0, HEIGHT)), "stop_distance": 0, "shoot_interval": 6200, "bullet_speed": 8, "shoot_pattern": "direct", "bullet_color": (75, 172, 0), "bullet_radius": 7, "speed": 1.67, "en_hp": 190},
    {"num": 12, "xy": (random.randint(0, WIDTH), random.randint(0, HEIGHT)), "stop_distance": 0, "shoot_interval": 5400, "bullet_speed": 7, "shoot_pattern": "wave", "bullet_color": (0, 0, 255), "bullet_radius": 8, "speed": 2.3, "en_hp": 140},
    {"num": 13, "xy": (random.randint(0, WIDTH), random.randint(0, HEIGHT)), "stop_distance": 0, "shoot_interval": 8700, "bullet_speed": 8, "shoot_pattern": "random", "bullet_color": (255, 174, 0), "bullet_radius": 6, "speed": 1.22, "en_hp": 130},
]

    enemies = []
    for i in range(10):  # 敵の数を設定
        settings = random.choice(base_enemy_settings).copy()  # base_enemy_settingsから設定をランダムに選択
        settings["xy"] = (random.randint(0, WIDTH), random.randint(0, HEIGHT))  # ランダムな位置
        enemy = Enemy(**settings)  # 必要な引数をすべて渡してインスタンス生成
        enemies.append(enemy)
    enemies = pg.sprite.Group(enemies)  # Groupにリストとして追加

    all_sprites = pg.sprite.Group()
    all_sprites.add(bird)
    all_sprites.add(*enemies)

    #enemy_manager = EnemyManager(all_sprites, enemies)


    en_bullets = pg.sprite.Group()

    start_time = pg.time.get_ticks()

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
        
        # マウスの現在位置を取得
        # mouse_pos = pg.mouse.get_pos()
        # こうかとんの更新
        # bird.update(mouse_pos)
        haikei.update(bird.rect)

        # 画面の更新
        # scfreen.fill((50, 50, 50))
        haikei.draw(screen)
        # all_sprites.draw(screen)

        if game_state == "playing":
            # マウスの現在位置を取得
            mouse_pos = pg.mouse.get_pos()
            # こうかとんの更新
            game_state = bird.update(mouse_pos, en_bullets)  # Update bird and check game state
            for enemy in enemies:
                enemy.update(bird.rect.center)
                # 敵が一定距離に達したら弾を発射
                current_time = pg.time.get_ticks()
                new_bullets = enemy.shoot(bird.rect.center, current_time, en_bullets)
                en_bullets.add(*new_bullets)
            
            # 1番近い敵を探す
            if enemies:
                closest_enemy = min(enemies, key=lambda e: math.hypot(e.rect.centerx - bird.rect.centerx, e.rect.centery - bird.rect.centery))
                if bullet_timer <= 0:
                    bullet = Bullet(bird.rect.center, closest_enemy.rect.center)
                    bullets.add(bullet)
                    all_sprites.add(bullet)
                    bullet_timer = 30  # 弾発射の間隔フレーム

            # 弾と敵の衝突判定
            for bullet in pg.sprite.groupcollide(bullets, enemies, True, False).keys():
                exp = closest_enemy.hit()
                if exp:
                    xp.value += 50
                    if xp.value >= 100:
                        bird.recover_hp()
                        xp.value = 0

            # 主人公が敵に接触した時ときのダメージ
            if pg.sprite.spritecollide(bird, enemies, False):
                bird.take_damage()
                if bird.hp <= 0:
                    game_state = "gameover"                   
                    #game_over_time = pg.time.get_ticks()  # ゲームオーバー時刻を記録

            # 更新処理
            # screen.fill((50, 50, 50))  # 画面の更新
            mouse_pos = pg.mouse.get_pos()
            bird.update(mouse_pos, en_bullets)
            enemies.update(bird.rect.center)
            en_bullets.update()
            # screen.fill((50, 50, 50))
            all_sprites.draw(screen)
            en_bullets.draw(screen)
            #enemy_manager.update()
            bullet_timer -= 1
 
            elapsed_time = (pg.time.get_ticks() - start_time) / 1000 # 秒単位に変換 
            time_text = font.render(f"Time: {elapsed_time:.2f}", True, (255, 255, 255))

            # 画面の更新
            #screen.fill((50, 50, 50))
            # 背景をループ表示
            # for x in range(-WIDTH, WIDTH * 2, background_image.get_width()):
            #     screen.blit(background_image, (x, 0))
            
            all_sprites.draw(screen)
            bullets.update()
            bullets.draw(screen)
            screen.blit(time_text, (10, 50))

            #  HP
            hp_text = font.render(f"HP: {bird.hp}", True, (0, 255, 255))
            screen.blit(hp_text, (10, 10))

            xp.update(screen)
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

        print(en_bullets)

        pg.display.update()
        tmr += 1        
        clock.tick(60)  # FPS:60



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
