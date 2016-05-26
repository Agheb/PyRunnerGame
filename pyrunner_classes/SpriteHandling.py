import pygame
import sre_constants

class SpriteSheet(object)
    """Class that grabs image from sprite sheet"""

    def __init__(self, filename):
        self.spritesheet = pygame.image.load("Spritesheet_LR.png").convert()

    def get_image