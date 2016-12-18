import pygame
import copy


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
        '''
        if self.rect.x > 0 and self.rect.x < SCREENWIDTH - self.image.get_width():
            self.rect.x += self.change_x
        elif self.rect.x <= 0:
            self.rect.x = 1
        elif self.rect.x >= SCREENWIDTH - self.image.get_width():
            self.rect.x = SCREENWIDTH - self.image.get_width() - 1
        '''
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

        width = 20
        height = 20
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
            self.rect.y += 20
            self.change_x *= -1
            self.reverseNext = False
        elif self.moveNext:
            self.rect.x += self.change_x
            self.moveNext = False

    def move(self):
        self.moveNext = True


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        width = 5
        height = 10
        self.image = pygame.Surface([width, height])
        self.image.fill(DARKORANGE)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.change_y = -9

        level = None

    def update(self):
        self.rect.y += self.change_y


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, bulletGroup):
        super().__init__()

        width = 80
        height = 20
        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = 100
        self.bullets = bulletGroup

    def update(self):
        # hit = pygame.sprite.collide_rect(self, self.bullets)
        # if hit:
        #     self.health -= 10
        for bullet in self.bullets:
            if pygame.sprite.collide_rect(self, bullet):
                bullet.kill()
                self.health -= 20

        if self.health <= 0:
            self.kill()

class Level():

    def __init__(self, player):
        self.wall_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.bullet_list = pygame.sprite.Group()
        self.player = player
        self.updates = 0
        self.lastReverse = 0
        self.reverseEnemies = False

    def update(self):
        self.updates += 1
        self.reverseEnemies = False

        if (self.updates - self.lastReverse > 60):
            for enemy in self.enemy_list:
                if enemy.rect.x < 40 or enemy.rect.x > SCREENWIDTH - 40:
                    self.reverseEnemies = True
                    self.lastReverse = copy.copy(self.updates)
                    break

        if self.reverseEnemies:
            for enemy in self.enemy_list:
                enemy.reverseNext = True

        self.wall_list.update()
        self.enemy_list.update()
        self.bullet_list.update()
        for bullet in self.bullet_list:
            if bullet.rect.y > SCREENHEIGHT:
               bullet.kill() 

        killdict = pygame.sprite.groupcollide(self.enemy_list, self.bullet_list, True, True)
        self.player.score += len(killdict)

    def draw(self, screen):
        screen.fill(BLACK)

        self.wall_list.draw(screen)
        self.enemy_list.draw(screen)
        self.bullet_list.draw(screen)

    def player_shoot(self):
        self.bullet_list.add(Bullet(self.player.rect.x + self.player.image.get_width() / 2, self.player.rect.y))


class MainLevel(Level):

    def __init__(self, player):
        Level.__init__(self, player)

        # enemies = []
        enemyRows = 3
        enemySpacing = 40
        wallCount = 4

        for i in range(enemyRows):
            for j in range(int((SCREENWIDTH - 200) / enemySpacing)):
                self.enemy_list.add(Enemy((j + 1)*enemySpacing, (i + 1)*50))

        # self.wall_list.add(Wall(50, 50, self.bullet_list))
        wallSpacing = (SCREENWIDTH - 100) / (wallCount)
        for i in range(wallCount):
            self.wall_list.add(Wall(int((i) * wallSpacing) + 100, (SCREENHEIGHT - 100), self.bullet_list))



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
    
    font = pygame.font.SysFont("monospace", 15)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_SPACE:
                    current_level.player_shoot()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()

            if event.type == pygame.USEREVENT + 1:
                for enemy in current_level.enemy_list:
                    enemy.move()


        active_sprite_list.update()
        current_level.update()

        current_level.draw(screen)
        active_sprite_list.draw(screen)
        text = font.render(str(player.score), 1, WHITE)
        screen.blit(text, (SCREENWIDTH - 30, 30))

        clock.tick(60)

        pygame.display.flip()


    pygame.quit()

if __name__ == "__main__":
    main()
