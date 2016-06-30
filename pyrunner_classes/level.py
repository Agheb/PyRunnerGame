#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main pyRunner class which initializes all sub classes and threads"""
# Python 2 related fixes
from __future__ import division
import pytmx
from pytmx.util_pygame import load_pygame
from .level_objecs import *
from .player import Player
import logging

log = logging.getLogger("Level")
LEVEL_PATH = "./resources/levels/"
LEVEL_EXT = ".tmx"

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
    PLAYER1 = "LRCharacters32.png"
    PLAYER2 = "LRCharacters32_p2.png"
    SM_SIZE = 32

    levels = []
    players = []

    def __init__(self, surface, path, fps=25):
        self.surface = surface
        self.background = self.surface.copy()
        self.path = path
        self.fps = fps
        self.tm = load_pygame(self.path, pixelalpha=True)
        self.tile_width, self.tile_height = self.tm.tilewidth, self.tm.tileheight
        self.tm_width = self.tm.width * self.tile_width
        self.tm_height = self.tm.height * self.tile_height
        self.width, self.height = self.tm_width, self.tm_height
        self.pixel_diff = 0
        self.margin_left = 0
        self.margin_top = 0
        s_width, s_height = surface.get_size()

        if self not in Level.levels:
            Level.levels.append(self)

        if self.tm_height is not s_height or self.tm_width is not s_width:
            '''automatically scale the tilemap'''
            diff_h = (s_height - self.tm_height) // self.tm.height
            diff_w = (s_width - self.tm_width) // self.tm.width

            self.pixel_diff = diff_h if diff_h < diff_w else diff_w
            self.tile_width += self.pixel_diff
            self.tile_height += self.pixel_diff
            self.width = self.tm.width * self.tile_width
            self.height = self.tm.height * self.tile_height
            self.margin_left = (s_width - self.width) // 2
            self.margin_top = (s_height - self.height) // 2
            # print(str(self.width), " ", str(self.height), " ", str(self.margin_left), " ", str(self.margin_top))

        '''draw the complete level'''
        self.render()

        try:
            p1_obj = self.tm.get_object_by_name("Player_1")
            p1_pos = self.calc_object_pos((p1_obj.x, p1_obj.y))
        except ValueError:
            p1_pos = 0, 0
        try:
            p2_obj = self.tm.get_object_by_name("Player_2")
            p2_pos = self.calc_object_pos((p2_obj.x, p2_obj.y))
        except ValueError:
            x, y = p1_pos
            p2_pos = x + 32, y
        try:
            next_level = self.tm.get_object_by_name("Exit_Gate")
            self.next_level_pos = self.calc_object_pos((next_level.x, next_level.y))
            self.next_level = LEVEL_PATH + next_level.type + LEVEL_EXT
        except ValueError:
            pass

        self.player_1_pos = p1_pos
        self.player_2_pos = p2_pos

    def calc_object_pos(self, pos_pixel):
        """adjust pixels to scaled tile map"""
        x, y = pos_pixel
        x //= self.tm.tilewidth
        y //= self.tm.tileheight
        x *= self.tile_width
        y *= self.tile_height
        x += self.margin_left
        y += self.margin_top

        return x, y

    def render(self):
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
                '''first check all layer properties'''
                ladder = check_property(layer, 'climbable')
                rope = check_property(layer, 'climbable_horizontal')
                gold = check_property(layer, 'collectible')
                removable = check_property(layer, 'removable')
                solid = check_property(layer, 'solid')
                width, height = self.tile_width, self.tile_height
                fps = self.fps

                '''create the sprites'''
                for a in layer.tiles():
                    pos_x, pos_y, image = a
                    size = width, height

                    pos_x = self.margin_left + (width * pos_x)
                    pos_y = self.margin_top + (height * pos_y)
                    image = pygame.transform.scale(image, size)

                    a = pos_x, pos_y, image

                    if ladder:
                        Ladder(a, size, fps, solid)
                    elif rope:
                        Rope(a, size, fps)
                    elif gold:
                        Collectible(a, size, fps)
                    elif removable:
                        WorldObject(a, size, fps, solid, removable)
                    elif solid:
                        WorldObject(a, size, fps, solid)

                    if layer.name == "Background":
                        '''create a blank copy of the background layer'''
                        self.render_tile(self.background, a)
                        self.render_tile(self.surface, a)

    @staticmethod
    def render_tile(surface, tile):
        """draw single tile"""
        x, y, image = tile

        surface.blit(image, (x, y))

    def clean_sprite(self, sprite):
        """overdraw an old sprite with a clean background"""
        # clear the item
        dirty_rect = self.background.subsurface(sprite.rect)
        self.surface.blit(dirty_rect, sprite.rect)
        # self.lvl_surface.blit(dirty_rect, sprite.rect)

    def add_player(self, pid, pos=None, fps=25):
        """add a new player"""
        pid = int(pid)

        if pid % 2 is 0:
            pos = self.player_1_pos if not pos else pos
            sheet = self.PLAYER1
        else:
            pos = self.player_2_pos if not pos else pos
            sheet = self.PLAYER2

        new_player = Player(pos, sheet, pid, self.SM_SIZE, self, self.fps)
        Level.players.append(new_player)
        log.info("Added Player. Players {}".format(Level.players))

    @staticmethod
    def get_level_info_json():
        # TODO: finish me
        a = []
        for d in Level.players:
            a.append(d.rect.topleft)
        data = {'players': a}
        return data

    @staticmethod
    def set_level_info_via_json(self, json):
        pass