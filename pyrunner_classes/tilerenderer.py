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



    def render(self, surface):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                self.render_tile_layer(surface, layer)

    def render_tile_layer(self, surface, layer):

        tw = self.tmx_data.tilewidth
        th = self.tmx_data.tileheight

        # iterate over the tiles in the layer
        for x, y, image in layer.tiles():
            surface.blit(image, (x * tw, y * th))
        # TODO iterate over object layer
        # TODO iterate over imageLayer

    def make_level(self):
        temp_surface = pygame.Surface(self.size)
        self.render(temp_surface)
        return temp_surface
