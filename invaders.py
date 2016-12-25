import pygame
import copy
import random


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARKORANGE = (255, 140, 0)

SCREENWIDTH = 800
SCREENHEIGHT = 600

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
    
        width = 40
        height = 40
        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)

        self.rect = self.image.get_rect()

        self.change_x = 0
        self.score = 0

        self.level = None

    def update(self):
        checkX = self.rect.x + self.change_x
        if not (checkX < 0 or checkX > SCREENWIDTH - self.image.get_width()):
                self.rect.x = checkX

    def go_left(self):
        self.change_x = -6

    def go_right(self):
        self.change_x = 6

    def stop(self):
        self.change_x = 0


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        width = 40
        height = 40
        self.image = pygame.Surface([width, height])
        self.image.fill(RED)

        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        self.change_x = 10

        self.moveNext = False
        self.reverseNext = False
    
    def update(self):
        if self.reverseNext:
            self.rect.y += 50
            self.change_x *= -1
            self.reverseNext = False
        elif self.moveNext:
            self.rect.x += self.change_x
            self.moveNext = False

    def move(self):
        self.moveNext = True


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, width = 5, height = 10):
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(DARKORANGE)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.change_y = -15

        level = None

    def update(self):
        self.rect.y += self.change_y


class EnemyBullet(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y, width = 12, height = 25)
        self.change_y *= -1
        self.change_y /= 1.5 


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        width = 80
        height = 20
        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = 100

    def update(self):
        if self.health <= 0:
            self.kill()


class Level():
    def __init__(self, player):
        self.wall_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.bullet_list = pygame.sprite.Group()
        self.player = player
        self.playerAlive = True
        self.updates = 0
        self.lastReverse = 0
        self.reverseEnemies = False

    def update(self):
        self.updates += 1
        self.reverseEnemies = False

        if (self.updates - self.lastReverse > 60):
            for enemy in self.enemy_list:
                if enemy.rect.x < 20 or enemy.rect.x > SCREENWIDTH - 60:
                    self.reverseEnemies = True
                    self.lastReverse = copy.copy(self.updates)
                    break

        if self.reverseEnemies:
            for enemy in self.enemy_list:
                enemy.reverseNext = True

        for wall in self.wall_list:
            for bullet in self.bullet_list:
                if pygame.sprite.collide_rect(wall, bullet):
                    bullet.kill()
                    wall.health -= 20

        self.wall_list.update()
        self.enemy_list.update()
        self.bullet_list.update()
        for bullet in self.bullet_list:
            if bullet.rect.y > SCREENHEIGHT:
               bullet.kill() 

        killdict = pygame.sprite.groupcollide(self.enemy_list, self.bullet_list, True, True)
        self.player.score += len(killdict)

        for bullet in self.bullet_list:
            if pygame.sprite.collide_rect(self.player, bullet):
                bullet.kill()
                self.playerAlive = False
                break

    def draw(self, screen):
        screen.fill(BLACK)

        self.wall_list.draw(screen)
        self.enemy_list.draw(screen)
        self.bullet_list.draw(screen)

    def player_shoot(self):
        self.bullet_list.add(Bullet(self.player.rect.x + self.player.image.get_width() / 2, self.player.rect.y))

    def enemy_shoot(self, x, y):
        self.bullet_list.add(EnemyBullet(x + 20, y + 45))


class MainLevel(Level):
    def __init__(self, player):
        Level.__init__(self, player)

        enemyRows = 3
        enemySpacing = 60
        wallCount = 4

        for i in range(enemyRows):
            for j in range(int((SCREENWIDTH - 200) / enemySpacing)):
                self.enemy_list.add(Enemy((j + 1)*enemySpacing, (i + 1) * enemySpacing))

        wallSpacing = (SCREENWIDTH - 100) / (wallCount)
        for i in range(wallCount):
            self.wall_list.add(Wall(int((i) * wallSpacing) + 100, (SCREENHEIGHT - 100)))


def gameOver(screen, score):
    font = pygame.font.SysFont("monospace", 40)
    sadText = font.render("Game Over", 1, WHITE)
    scoreText = font.render("Score: " + str(score), 1, WHITE)
    screen.blit(sadText, (SCREENWIDTH / 2, SCREENHEIGHT / 2))
    screen.blit(scoreText, (SCREENWIDTH / 2, SCREENHEIGHT / 2 + 50))


def main():
    pygame.init()

    size = [SCREENWIDTH, SCREENHEIGHT]
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Space Invaders")

    player = Player()

    current_level = MainLevel(player)

    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    player.rect.x = 50
    player.rect.y = SCREENHEIGHT - player.rect.height - 20
    active_sprite_list.add(player)

    done = False
    clock = pygame.time.Clock()
    pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
    pygame.time.set_timer(pygame.USEREVENT + 2, 2000)
    
    font = pygame.font.SysFont("monospace", 15)
    lastShot = 0

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_SPACE and pygame.time.get_ticks() - lastShot > 700:
                    current_level.player_shoot()
                    lastShot = pygame.time.get_ticks()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()

            if event.type == pygame.USEREVENT + 1:
                lowestEnemies = {}
                if random.randint(1, 2) == 1:
                    for enemy in current_level.enemy_list:
                        if enemy.rect.x not in lowestEnemies:
                            lowestEnemies[enemy.rect.x] = enemy
                        else:
                            if lowestEnemies[enemy.rect.x].rect.y < enemy.rect.y:
                                lowestEnemies[enemy.rect.x] = enemy

                    keylist = list(lowestEnemies.keys())
                    randEnemy = lowestEnemies[random.choice(keylist)]

                    if (len(keylist) / random.randint(1, 10)) >= 1:
                        current_level.enemy_shoot(randEnemy.rect.x, randEnemy.rect.y)

                for enemy in current_level.enemy_list:
                    enemy.move()

        active_sprite_list.update()
        current_level.update()

        current_level.draw(screen)
        active_sprite_list.draw(screen)
        text = font.render(str(player.score), 1, WHITE)
        screen.blit(text, (SCREENWIDTH - 30, 30))

        if len(current_level.enemy_list) == 0:
            wallTemp = current_level.wall_list
            current_level = MainLevel(player)
            current_level.wall_list = wallTemp

        if not current_level.playerAlive:
            screen.fill(BLACK)
            gameOver(screen, player.score)
            pygame.display.flip()
            done = True
            pygame.time.wait(4000)

        clock.tick(60)

        pygame.display.flip()
        
    pygame.quit()


if __name__ == "__main__":
    main()
