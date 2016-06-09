"""
Level Builder for PyRunner game
PyTMX is used to load tilemap into game
Level-Editor: Tiled
TMX ( Tiled Map XML) to describe a map
TMX- Specification:
"""

#TODO TMX Specification:
#TODO make collidable Rects from ObjectLayers


import pytmx
import pygame
from pprint import pprint
from .game_physics import *
from pytmx.util_pygame import load_pygame


class Level(object):

    """
    Level object loads tmx-file for game and draws each tile to screen
    filename: Tilesheet and TMX-File must be in same folder
    1. Read in and parse TMX file
    2. load all tilesheet image
    3. draw layer by layer
    """

    def __init__(self, filename, surface):
        tm = load_pygame(filename, pixelalpha=True)
        self.size = tm.width * tm.tilewidth, tm.height * tm.tileheight
        self.tm = tm
        self.surface = surface
        self.render(self.surface)

    def render(self, surface):
        for layer in self.tm.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                self.render_tile_layer(surface, layer)
                if layer.properties['solid'] == 'true':
                    for a in layer.tiles():
                        WorldObject(a)
                if layer.properties['climbable'] == 'true':
                    for a in layer.tiles():
                        WorldObject(a,True)
                #pprint(layer.properties)

    def render_tile_layer(self, surface, layer):

        tw = self.tm.tilewidth
        th = self.tm.tileheight

        # iterate over the tiles in the layer
        for x, y, image in layer.tiles():
            surface.blit(image, (x * tw, y * th))
        # TODO iterate over object layer
        # TODO iterate over imageLayer

    def make_level(self):
        temp_surface = pygame.Surface(self.size)
        self.render(temp_surface)
        return temp_surface
