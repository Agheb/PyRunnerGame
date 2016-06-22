"""
This module is used to pull individual sprites from sprite sheets.
"""
import pygame
from .constants import *


class SpriteSheet(object):
    """ Class used to grab images out of a sprite sheet. """

    def __init__(self, file_name, tilesize, fps=25):
        """ Constructor. Pass in the file name of the sprite sheet. """
        # Load the sprite sheet.
        self.sprite_sheet = pygame.image.load(file_name).convert()
        self.tile_size = tilesize
        self.fps = fps

    def get_image(self, x, y, width, height):
        """ Grab a single image out of a larger spritesheet
            Pass in the x, y location of the sprite
            and the width and height of the sprite. """

        # Create a new blank image
        image = pygame.Surface([width, height]).convert()

        # Copy the sprite from the large sheet onto the smaller image
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))

        # Assuming black works as the transparent color
        image.set_colorkey(BLACK)

        # Return the image
        return image

    def add_animation(self, pos_x, pos_y, list=None, frames=1, flip=False):
        """define which images on a sprite sheet to use for an animation"""
        ts = self.tile_size
        pos_y *= ts

        try:
            for i in range(frames):
                image = self.get_image(pos_x, pos_y, ts, ts)
                if flip:
                    image = pygame.transform.flip(image, True, False)
                list.append(image)
                pos_x += ts

            return list
        except AttributeError:
            return self.get_image(pos_x * ts, pos_y * ts, ts, ts)

    def get_frame(self, position, frame_list):
        """returns the next frame in order"""
        position = (position // self.fps) % len(frame_list)
        return frame_list[position]
