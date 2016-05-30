import pygame
from pygame.locals import *
from .SpriteHandling import *


WHITE = (255, 255, 255)


class Player(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, width, height):
        super.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(sprite).convert_alpha(), (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y

        """List holding image for moving left/right"""
        self.walking_frames_l = []
        self.walking_frames_r = []

        # direction player is facing
        self.direction = "R"

        sprite_sheet = SpriteSheet("Spritesheet_LR.png")
        image = sprite_sheet.get_image(0, 0, 66, 90)
        self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(66, 0, 66, 90)
        self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(132, 0, 67, 90)
        self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(0, 93, 66, 90)
        self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(66, 93, 66, 90)
        self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(132, 93, 72, 90)
        self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(0, 186, 70, 90)
        self.walking_frames_r.append(image)

        # Load all the right facing images, then flip them
        # to face left.
        image = sprite_sheet.get_image(0, 0, 66, 90)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)
        image = sprite_sheet.get_image(66, 0, 66, 90)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)
        image = sprite_sheet.get_image(132, 0, 67, 90)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)
        image = sprite_sheet.get_image(0, 93, 66, 90)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)
        image = sprite_sheet.get_image(66, 93, 66, 90)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)
        image = sprite_sheet.get_image(132, 93, 72, 90)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)
        image = sprite_sheet.get_image(0, 186, 70, 90)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)

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
    pygame.draw.circle(screen, WHITE, (140, 120), 20, 0)


    pygame.display.update()
    fpsclock.tick(20)
