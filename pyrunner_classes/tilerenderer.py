'''
First test to work with pytmx and a render
'''

import pygame
import pytmx
from pytmx.util_pygame import load_pygame


class Renderer(object):
    """
    This object renders tile maps from Tiled
    """
    def __init__(self, filename):
        tm = load_pygame(filename, pixelalpha=True)
        self.size = tm.width * tm.tilewidth, tm.height * tm.tileheight
        self.tmx_data = tm

    ## TODO loop through each tile and blit to screen

    def render(self, surface):
        pass

    def make_level(self):
        temp_surface = pygame.Surface(self.size)
        self.render(temp_surface)
        return temp_surface
