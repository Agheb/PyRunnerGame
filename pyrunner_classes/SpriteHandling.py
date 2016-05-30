import pygame
import sre_constants

# Colors
BLUE = (30, 144, 255)
YELLOW = (255, 255, 0)
RED = (100, 0, 0)
BLACK = (0, 0, 0)
BACKGROUND = (100, 100, 100)
GRAY = (150, 150, 150)
WHITE = (255, 255, 255)


class SpriteSheet(object):
    """Class that grabs image from sprite sheet"""

    def __init__(self, filename):
        self.spritesheet = pygame.image.load(filename).convert()

    def getimage(self, x, y, width, height):
        image = pygame.Surface([width, height]).convert()  # create new blank image
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))  # copy sprite to blank image
        image.set_colorkey(sre_constants.WHITE)  # set transparent color
        return image

