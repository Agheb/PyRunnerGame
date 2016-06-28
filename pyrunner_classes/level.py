#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main pyRunner class which initializes all sub classes and threads"""
# Python 2 related fixes
from __future__ import division
import pygame
import pytmx
from pytmx.util_pygame import load_pygame
from pygame.locals import *
from .spritesheet_handling import *

LEVEL_PATH = "./resources/levels/"
LEVEL_EXT = ".tmx"
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
        self.tm = load_pygame(LEVEL_LIST[level_number], pixelalpha=True)
        self.tile_width, self.tile_height = self.tm.tilewidth, self.tm.tileheight
        self.tm_width = self.tm.width * self.tile_width
        self.tm_height = self.tm.height * self.tile_height
        self.width, self.height = self.tm_width, self.tm_height
        self.pixel_diff = 0
        self.margin_left = 0
        self.margin_top = 0
        s_width, s_height = surface.get_size()

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

        self.surface = surface
        self.background = self.surface.copy()
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

                '''create the sprites'''
                for a in layer.tiles():
                    pos_x, pos_y, image = a
                    size = width, height

                    pos_x = self.margin_left + (width * pos_x)
                    pos_y = self.margin_top + (height * pos_y)
                    image = pygame.transform.scale(image, size)

                    a = pos_x, pos_y, image

                    if ladder:
                        Ladder(a, size, solid)
                    elif rope:
                        Rope(a, size)
                    elif gold:
                        Collectible(a, size)
                    elif removable:
                        WorldObject(a, size, solid, removable)
                    elif solid:
                        WorldObject(a, size, solid)

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


class WorldObject(pygame.sprite.DirtySprite):
    """hello world"""

    group = pygame.sprite.LayeredDirty(default_layer=-1)
    removed = pygame.sprite.LayeredDirty(default_layer=0)

    def __init__(self, tile, size, solid=True, removable=False, restoring=False):
        """world object item"""
        pygame.sprite.DirtySprite.__init__(self, WorldObject.group)
        self.tile = tile
        self.size = size
        self.width, self.height = self.size
        self.pos_x, self.pos_y, self.image_backup = self.tile
        self.rect = self.image_backup.get_rect()
        self.rect.x = self.pos_x
        self.rect.y = self.pos_y
        self.solid = solid
        self.removable = removable
        self.climbable = False
        self.climbable_horizontal = False
        self.collectible = False
        self.killed = False
        self.restoring = restoring
        self.exit = False

        if restoring:
            self.image = pygame.Surface((self.width, self.height), SRCALPHA)
            self.rect.y += self.height
            self.rect.height = 0
        else:
            self.image = self.image_backup

    def update(self):
        """update world objects"""
        if self.killed or self.restoring:
            x, y = self.rect.topleft
            w, h = self.rect.size
            if self.restoring:
                y -= 2
                h += 2
            elif self.removable:
                y += 2
                h -= 2
            elif self.collectible:
                x += 4
                y += 4
                w -= 8
                h -= 8

            if (h <= 0 or w <= 0) and self.killed:
                self.super_kill()
            elif h >= self.height and self.restoring:
                self.image = self.image_backup
                self.rect.x = self.pos_x
                self.rect.y = self.pos_y
                self.restoring = False
            else:
                rect = pygame.Rect(x, y, w, h)
                self.image = pygame.transform.scale(self.image_backup, (w, h)).convert_alpha()
                self.rect = rect

            self.dirty = 1

    def kill(self):
        """remove this sprite"""
        if self.removable or self.collectible:
            if not self.killed and self.removable:
                RemovedBlock(self.tile, self.rect.size, 4)
            self.killed = True
        else:
            self.super_kill()

    def super_kill(self):
        """call the parent class kill function"""
        pygame.sprite.DirtySprite.kill(self)


class Ladder(WorldObject):
    """climbable ladder"""

    def __init__(self, tile, size, solid=False):
        WorldObject.__init__(self, tile, size, solid)
        self.climbable = True


class Rope(WorldObject):
    """hangable rope"""
    def __init__(self, tile, size):
        WorldObject.__init__(self, tile, size)
        self.climbable_horizontal = True


class Collectible(WorldObject):
    """collectible gold"""
    def __init__(self, tile, size):
        WorldObject.__init__(self, tile, size)
        self.collectible = True


class RemovedBlock(pygame.sprite.DirtySprite):
    """store values of removed blocks to restore them later on"""
    def __init__(self, tile, size, time_out, fps=25):
        pygame.sprite.DirtySprite.__init__(self, WorldObject.removed)
        self.tile = tile
        self.size = size
        self.width, self.height = self.size
        self.pos_x, self.pos_y, self.restore_image = self.tile
        self.image = pygame.Surface(size, SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = self.pos_x
        self.rect.y = self.pos_y
        self.time_out = time_out
        self.fps = fps
        self.counter = 0
        self.trapped = False

    def update(self):
        """countdown on each update until the object get's restored"""
        self.counter += 1

        if self.counter is self.fps * self.time_out:
            self.restore()
            self.kill()

    def restore(self):
        """recreate a sprite with the same values"""
        return WorldObject(self.tile, self.size, True, True, True)


class ExitGate(WorldObject):
    """let's the player return to the next level"""
    def __init__(self, pos, sheet, size, pixel_diff=0, fps=25):
        self.sprite_sheet = SpriteSheet(sheet, size, pixel_diff * 2 + size, fps)
        self.animation = self.sprite_sheet.add_animation(8, 4, 4)
        self.counter = 0
        self.fps = fps
        self.image = self.sprite_sheet.get_frame(0, self.animation)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        tile = self.rect.x, self.rect.y, self.image
        WorldObject.__init__(self, tile, (size, size), True)
        self.exit = True
        self.spawned = False
        self.killed = False

    def update(self):
        """play glowing animation"""
        lenght = len(self.animation) - 1

        if not self.spawned:
            self.image = self.animation[self.counter // 5]

            if self.counter is lenght * 5:
                self.spawned = True

            self.counter += 1
            self.dirty = 1
