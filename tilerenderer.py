'''
First test to work with pytmx and a render
'''

import pygame
from pyrunner_classes import pytmx
from pyrunner_classes import util_pygame


class Renderer(object):
    """
    This object renders tile maps from Tiled
    """
    def __init__(self, filename):
        tm = util_pygame.load_pygame(filename, pixelalpha=True)
        self.size = tm.width * tm.tilewidth, tm.height * tm.tileheight
        self.tmx_data = tm

    def render(self, surface):

        tw = self.tmx_data.tilewidth
        th = self.tmx_data.tileheight
        gt = self.tmx_data.getTileImageByGid

        if self.tmx_data.background_color:
            surface.fill(self.tmx_data.background_color)

        for layer in self.tmx_data.visibleLayers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = gt(gid)
                    if tile:
                        surface.blit(tile, (x * tw, y * th))

            elif isinstance(layer, pytmx.TiledObjectGroup):
                pass

            elif isinstance(layer, pytmx.TiledImageLayer):
                image = gt(layer.gid)
                if image:
                    surface.blit(image, (0, 0))

    def make_level(self):
        temp_surface = pygame.Surface(self.size)
        self.render(temp_surface)
        return temp_surface
