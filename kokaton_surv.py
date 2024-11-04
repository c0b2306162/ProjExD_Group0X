import os
import sys
import pygame as pg
import random
import math

# ゲームの初期設定
WIDTH, HEIGHT = 1800, 1000
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ゲームキャラクター（主人公、敵、弾、経験値）に関するクラス
class Bird(pg.sprite.Sprite):
    def __init__(self, num: int, xy: tuple[int, int]):
        """
        引数１ num：こうかとん画像ファイル名の番号
        引数２ xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img = pg.image.load(f"fig/{num}.png")
        self.image = pg.transform.scale(img, (60, 60))
        self.rect = self.image.get_rect(center=xy)
        self.speed = 5
        self.exp = 0  # 経験値

    def update(self, target):
        dx, dy = target[0] - self.rect.centerx, target[1] - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance > 0:
            dx, dy = dx / distance, dy / distance
            self.rect.centerx += dx * self.speed
            self.rect.centery += dy * self.speed

    def gain_exp(self, value):
        self.exp += value
        print(f"経験値: {self.exp}")

class Enemy(pg.sprite.Sprite):
    def __init__(self, xy: tuple[int, int]):
        super().__init__()
        self.image = pg.Surface((40, 40), pg.SRCALPHA)
        pg.draw.circle(self.image, (255, 0, 0), (20, 20), 20)
        self.rect = self.image.get_rect(center=xy)
        self.speed = 2
        self.health = 3

    def update(self, target):
        dx, dy = target[0] - self.rect.centerx, target[1] - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance > 0:
            dx, dy = dx / distance, dy / distance
            self.rect.centerx += dx * self.speed
            self.rect.centery += dy * self.speed

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
            return ExpOrb(self.rect.center)
        return None

class Bullet(pg.sprite.Sprite):
    def __init__(self, pos, target_pos):
        super().__init__()
        self.image = pg.Surface((10, 10), pg.SRCALPHA)
        pg.draw.circle(self.image, (0, 255, 255), (5, 5), 5)
        self.rect = self.image.get_rect(center=pos)
        dx, dy = target_pos[0] - pos[0], target_pos[1] - pos[1]
        distance = math.hypot(dx, dy)
        self.speed = 10
        self.velocity = (dx / distance * self.speed, dy / distance * self.speed)

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not (0 <= self.rect.x <= WIDTH and 0 <= self.rect.y <= HEIGHT):
            self.kill()

class ExpOrb(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pg.Surface((15, 15), pg.SRCALPHA)
        pg.draw.circle(self.image, (0, 255, 0), (7, 7), 7)
        self.rect = self.image.get_rect(center=pos)
        self.value = 10

#敵の再出現を管理するクラス
class EnemyManager:
    def __init__(self, all_sprites, enemies, respawn_time=300):
        self.all_sprites = all_sprites
        self.enemies = enemies
        self.respawn_time = respawn_time #　復活するまでのフレーム数
        self.respawn_timer = []

    def update(self):
        #敵の再出現を管理
        for idx, timer in enumerate(self.respawn_timer):
            self.respawn_timer[idx] -= 1
            if self.respawn_timer[idx] <= 0:
                self.respawn_timer.pop(idx)
                self.spawn_enemy()
        #敵の数を5～7体に保つ
        if len(self.enemies) < 5:
            self.spawn_enemy()

    def spawn_enemy(self):
        enemy = Enemy((random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)

    def schedule_respawn(self):
        if len(self.enemies) < 7:
            self.respawn_timer.append(self.respawn_time)

# ゲームのメインループ
def main():
    pg.display.set_caption("吸血鬼生存猪")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()

    # プレイヤーと敵の初期化
    bird = Bird(1, (WIDTH // 2, HEIGHT // 2))
    enemies = pg.sprite.Group(Enemy((random.randint(0, WIDTH), random.randint(0, HEIGHT))) for _ in range(5))
    bullets = pg.sprite.Group()
    exp_orbs = pg.sprite.Group()

    all_sprites = pg.sprite.Group(bird, *enemies)
    enemy_manager = EnemyManager(all_sprites, enemies)

    bullet_timer = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        # 1番近い敵を探す
        if enemies:
            closest_enemy = min(enemies, key=lambda e: math.hypot(e.rect.centerx - bird.rect.centerx, e.rect.centery - bird.rect.centery))
            if bullet_timer <= 0:
                bullet = Bullet(bird.rect.center, closest_enemy.rect.center)
                bullets.add(bullet)
                all_sprites.add(bullet)
                bullet_timer = 30  # 弾発射の間隔（フレーム）

        # 弾と敵の衝突判定
        for bullet in pg.sprite.groupcollide(bullets, enemies, True, False).keys():
            orb = closest_enemy.hit()
            if orb:
                exp_orbs.add(orb)
                all_sprites.add(orb)
                enemy_manager.schedule_respawn()


        # 経験値玉と主人公の衝突判定
        for orb in pg.sprite.spritecollide(bird, exp_orbs, True):
            bird.gain_exp(orb.value)

        # 更新処理
        mouse_pos = pg.mouse.get_pos()
        bird.update(mouse_pos)
        enemies.update(bird.rect.center)
        bullets.update()
        enemy_manager.update()
        
        bullet_timer -= 1

        # 画面更新
        screen.fill((30, 30, 30))
        all_sprites.draw(screen)
        pg.display.update()
        clock.tick(60)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
