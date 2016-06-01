import pygame
from spritesheet_handling import SpriteSheet

# These constants define our platform types:
#   X location of sprite
#   Y location of sprite
#   Width of sprite
#   Height of sprite

BRICKWALL = (0, 0, 16, 16)
LADDER = (32, 0, 15, 48)
WALL = (0, 16, 16, 16)


class Platform(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet_data):
        super().__init__()

        sprite_sheet = SpriteSheet("LRTileset.png")
        # Grab the image for this platform
        self.image = sprite_sheet.get_image(sprite_sheet_data[0],
                                            sprite_sheet_data[1],
                                            sprite_sheet_data[2],
                                            sprite_sheet_data[3])

        self.rect = self.image.get_rect()
