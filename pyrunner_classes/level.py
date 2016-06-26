#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main pyRunner class which initializes all sub classes and threads"""
# Python 2 related fixes
from __future__ import division
import pygame
import pytmx
from pytmx.util_pygame import load_pygame

MULTIPLICATOR = 1
TILE_WIDTH = 32
TILE_HEIGHT = 32
LEVEL_LIST = ["./resources/levels/scifi.tmx", "./resources/levels/level2.tmx",
                           "./resources/levels/level3.tmx"]

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

    def __init__(self, surface, level_number=0):
        self.level_id = level_number
        tm = load_pygame(LEVEL_LIST[level_number], pixelalpha=True)
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
            p2_pos = self.tm.get_object_by_name("Player_2")
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
        def check_property(current_layer, sprite_property):
            """check layer for a specific property and if it exists create the corresponding object"""
            try:
                if current_layer.properties[sprite_property] == 'true':
                    return True
                else:
                    return False
            except KeyError:
                return False

        for layer in self.tm.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                self.render_tile_layer(surface, layer)

                '''first check all layer properties'''
                ladder = check_property(layer, 'climbable')
                rope = check_property(layer, 'climbable_horizontal')
                gold = check_property(layer, 'collectible')
                removable = check_property(layer, 'removable')
                solid = check_property(layer, 'solid')

                '''create the sprites'''
                for a in layer.tiles():
                    if ladder:
                        Ladder(a, solid)
                    elif rope:
                        Rope(a)
                    elif gold:
                        Collectible(a)
                    elif removable:
                        WorldObject(a, solid, removable)
                    elif solid:
                        WorldObject(a, solid)

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

    def render_tile_layer(self, surface, layer):
        """draw single tile"""
        tw = self.tm.tilewidth
        th = self.tm.tileheight

        # iterate over the tiles in the layer
        for x, y, image in layer.tiles():
            surface.blit(image, (x * tw, y * th))
            # TODO iterate over object layer
            # TODO iterate over imageLayer

    def clean_sprite(self, sprite):
        """overdraw an old sprite with a clean background"""
        # clear the item
        dirty_rect = self.background.subsurface(sprite.rect)
        self.surface.blit(dirty_rect, sprite.rect)
        # self.lvl_surface.blit(dirty_rect, sprite.rect)


class WorldObject(pygame.sprite.DirtySprite):
    """hello world"""

    group = pygame.sprite.LayeredDirty(default_layer=-1)

    def __init__(self, tile, solid=True, removable=False):
        """world object item"""
        pygame.sprite.DirtySprite.__init__(self, WorldObject.group)
        (pos_x, pos_y, self.image) = tile
        self.rect = self.image.get_rect()
        self.rect.x = pos_x * TILE_WIDTH
        self.rect.y = pos_y * TILE_HEIGHT
        self.solid = solid
        self.removable = removable
        self.climbable = False
        self.climbable_horizontal = False
        self.collectible = False
        self.killed = False

    def update(self):
        """update world objects"""
        if self.killed:
            x, y = self.rect.topleft
            w, h = self.rect.size
            if self.removable:
                y += 2
                h -= 2
            elif self.collectible:
                x += 4
                y += 4
                w -= 8
                h -= 8
            rect = pygame.Rect(x, y, w, h)
            self.image = pygame.transform.scale(self.image, (w, h)).convert_alpha()
            self.rect = rect

            if h is 0:
                self.super_kill()

            self.dirty = 1

    def kill(self):
        """remove this sprite"""
        if self.removable or self.collectible:
            self.killed = True
        else:
            self.super_kill()

    def super_kill(self):
        """call the parent class kill function"""
        pygame.sprite.DirtySprite.kill(self)


class Ladder(WorldObject):
    """climbable ladder"""

    def __init__(self, tile, solid=False):
        WorldObject.__init__(self, tile, solid)
        self.climbable = True


class Rope(WorldObject):
    """hangable rope"""
    def __init__(self, tile):
        WorldObject.__init__(self, tile)
        self.climbable_horizontal = True


class Collectible(WorldObject):
    """collectible gold"""
    def __init__(self, tile):
        WorldObject.__init__(self, tile)
        self.collectible = True
