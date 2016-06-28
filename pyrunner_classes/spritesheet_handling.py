"""
This module is used to pull individual sprites from sprite sheets.
"""
import pygame
from .constants import *


SPRITE_SHEET_PATH = "./resources/sprites/"


class SpriteSheet(object):
    """ Class used to grab images out of a sprite sheet. """

    def __init__(self, file_name, tilesize, pixel_diff=0, fps=25):
        """ Constructor. Pass in the file name of the sprite sheet. """
        # Load the sprite sheet.
        self.sprite_sheet = pygame.image.load(SPRITE_SHEET_PATH + file_name).convert()
        self.tile_size = tilesize
        self.pixel_diff = pixel_diff
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

        if self.pixel_diff is not 0:
            width += self.pixel_diff
            height += self.pixel_diff
            image = pygame.transform.scale(image, (width, height))

        # Return the image
        return image

    def add_animation(self, pos_x, pos_y, frames=1,):
        """define which images on a sprite sheet to use for an animation"""
        ts = self.tile_size
        pos_y *= ts
        pos_x *= ts

        if frames is not 1:
            frame_list = []
            for i in range(frames):
                image = self.get_image(pos_x, pos_y, ts, ts)
                frame_list.append(image)
                pos_x += ts

            return frame_list
        else:
            return self.get_image(pos_x, pos_y, ts, ts)

    @staticmethod
    def flip_list(frames):
        """horizontal flip all frames in a list (make left movements to right etc)"""
        flipped_list = []

        for i in frames:
            image = pygame.transform.flip(i, True, False)
            flipped_list.append(image)

        return flipped_list

    def get_frame(self, position, frame_list, speed=1):
        """returns the next frame in order"""
        position = ((position // self.fps) * speed) % len(frame_list)
        return frame_list[position]
