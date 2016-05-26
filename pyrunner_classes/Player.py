import pygame
from pygame.locals import *

WHITE = (255, 255, 255)


class Player(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(sprite).convert_alpha(), (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y

    def bewegen_x(self, width):
        self.rect.x = self.rect.x + width

    def bewegen_y(self, width):
        self.rect.y = self.rect.y + width

# Optionen
screen_x = 500
screen_y = 500
gamename = "PyRunnerPlayer"
sprite = "stickmanBasic.png"

# Init pygame
pygame.init()
fenster = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption(gamename)
screen = pygame.display.get_surface()
player1 = Player(screen_x / 2, screen_y / 2, 60, 80)
playersprite = pygame.sprite.RenderPlain(player1)

# Variablen
width = False
fpsclock = pygame.time.Clock()
gameover = False

while not gameover:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == QUIT:
            gameover = True

    tastendruck = pygame.key.get_pressed()
    if tastendruck[K_LEFT]:
        player1.bewegen_x(-3)
    if tastendruck[K_RIGHT]:
        player1.bewegen_x(3)
    if tastendruck[K_UP]:
        player1.bewegen_y(-3)
    if tastendruck[K_DOWN]:
        player1.bewegen_y(3)
    if tastendruck[K_q]:
        gameover = True

    playersprite.draw(screen)

    pygame.display.update()
    fpsclock.tick(20)
