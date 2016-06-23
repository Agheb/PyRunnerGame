#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main pyRunner class which initializes all sub classes and threads"""
# Python 2 related fixes
from __future__ import division
import pytmx
from .game_physics import *
from .player import Player
from pytmx.util_pygame import load_pygame

"""
Level Builder for PyRunner game
PyTMX is used to load tilemap into game
Level-Editor: Tiled
TMX ( Tiled Map XML) to describe a map
TMX- Specification:
"""


# TODO TMX Specification:
# TODO make collidable Rects from ObjectLayers


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
        self.player_bg = surface.copy()
        self.background = surface.copy()
        self.render(self.surface)
        try:
            p1_pos = self.tm.get_object_by_name("Player_1")
            p1_x, p1_y = p1_pos.x, p1_pos.y
        except ValueError:
            p1_x, p1_y = 0, 0
        try:
            p2_pos = self.tm.get_object_by_name("Player_1")
            p2_x, p2_y = p2_pos.x, p2_pos.y
        except ValueError:
            p2_x, p2_y = 32, 0
        self.player_1_pos = p1_x, p1_y
        self.player_2_pos = p2_x, p2_y

    def render(self, surface):
        """Create the level. Iterates through the layers in the TMX (see game_physics WorldObjects).
         For each Objects the properties are set as follows with defaults:
         (self, tile, solid=True, climbable=False, climbable_horizontal=False)
         """
        for layer in self.tm.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                self.render_tile_layer(surface, layer)
                try:
                    if layer.properties['solid'] == 'true':
                        for a in layer.tiles():
                            WorldObject(a)
                except KeyError:
                    pass
                try:
                    if layer.properties['climbable'] == 'true':
                        for a in layer.tiles():
                            Ladder(a)
                            # print(layer.properties)
                except KeyError:
                    pass
                try:
                    if layer.properties['climbable_horizontal'] == 'true':
                        for a in layer.tiles():
                            Rope(a)
                            # print(layer.properties)
                except KeyError:
                    pass
                try:
                    if layer.properties['collectible'] == 'true':
                        for a in layer.tiles():
                            Collectible(a)
                            # print(layer.properties)
                except KeyError:
                    pass
                try:
                    if layer.name == "Background":
                        '''create a blank copy of the background layer'''
                        self.render_tile_layer(self.background, layer)
                except:
                    raise

        for group in self.tm.objectgroups:
            for obj in group:
                try:
                    if obj.name == "Player_1":
                        self.player_1_pos = obj.x, obj.y
                except (KeyError, AttributeError, ValueError):
                    pass

#        for layer in self.tm.invisible_layers:
#           if isinstance(layer, pytmx.TiledTileLayer):
#                self.render_tile_layer(surface, layer)
#                if layer.properties['collectible'] == 'true':
#                    for a in layer.tiles():
#                        RemovableWorldObjects(a, False, False, False, True)
#                        # print(layer.properties)

    def render_tile_layer(self, surface, layer):
        """draw single tile"""
        tw = self.tm.tilewidth
        th = self.tm.tileheight

        # iterate over the tiles in the layer
        for x, y, image in layer.tiles():
            surface.blit(image, (x * tw, y * th))
            # TODO iterate over object layer
            # TODO iterate over imageLayer

    def make_level(self):
        """draw the level to a surface"""
        temp_surface = pygame.Surface(self.size)
        self.render(temp_surface)
        return temp_surface
