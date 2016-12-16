import pygame


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

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


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        width = 5
        height = 10
        self.image = pygame.Surface([width, height])
        self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.change_y = -5

        level = None

    def update(self):
        self.rect.y += self.change_y


class Level():

    def __init__(self, player):
        self.wall_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.bullet_list = pygame.sprite.Group()
        self.player = player

    def update(self):
        self.wall_list.update()
        self.enemy_list.update()
        self.bullet_list.update()
        for bullet in self.bullet_list:
            if bullet.rect.y > SCREENHEIGHT:
               bullet.kill() 

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

        active_sprite_list.update()
        current_level.update()

        current_level.draw(screen)
        active_sprite_list.draw(screen)

        clock.tick(60)

        pygame.display.flip()


    pygame.quit()

if __name__ == "__main__":
    main()
