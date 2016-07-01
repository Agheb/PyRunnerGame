#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main pyRunner class which initializes all sub classes and threads"""
# Python 2 related fixes
from __future__ import division
from .spritesheet_handling import *


class WorldObject(pygame.sprite.DirtySprite):
    """hello world"""

    group = pygame.sprite.LayeredDirty(default_layer=0)
    removed = pygame.sprite.LayeredDirty(default_layer=0)

    def __init__(self, tile, size, tile_id, fps=25, solid=True, removable=False, restoring=False):
        """world object item"""
        '''the index is used to direct acces on network syncs'''
        self.index = len(WorldObject.group)
        pygame.sprite.DirtySprite.__init__(self, WorldObject.group)
        self.tile = tile
        self.size = size
        self.tile_id = tile_id
        self.fps = fps
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

    def update_indices(self):
        """update all group indexes for all objects that follow this one in the list"""
        for index, world_object in enumerate(WorldObject.group, self.index - 1):
            world_object.index = index

    def kill(self):
        """remove this sprite"""
        if self.removable or self.collectible:
            if not self.killed and self.removable:
                RemovedBlock(self.tile, self.rect.size, 4, self.fps)
            self.killed = True
        else:
            self.super_kill()
            '''always update the indices'''
            self.update_indices()

    def super_kill(self):
        """call the parent class kill function"""
        pygame.sprite.DirtySprite.kill(self)


class Ladder(WorldObject):
    """climbable ladder"""

    def __init__(self, tile, size, tile_id, fps, solid=False):
        WorldObject.__init__(self, tile, size, tile_id, fps, solid)
        self.climbable = True


class Rope(WorldObject):
    """hangable rope"""
    def __init__(self, tile, size, tile_id, fps):
        WorldObject.__init__(self, tile, size, tile_id, fps)
        self.climbable_horizontal = True


class Collectible(WorldObject):
    """collectible gold"""
    def __init__(self, tile, size, tile_id, fps):
        WorldObject.__init__(self, tile, size, tile_id, fps)
        self.collectible = True

    def kill(self):
        """remove the gold coin"""
        WorldObject.kill(self)


class RemovedBlock(pygame.sprite.DirtySprite):
    """store values of removed blocks to restore them later on"""
    def __init__(self, tile, size, tile_id, fps=25, time_out=1):
        pygame.sprite.DirtySprite.__init__(self, WorldObject.removed)
        self.tile = tile
        self.size = size
        self.tile_id = tile_id
        self.fps = fps
        self.time_out = time_out
        self.width, self.height = self.size
        self.pos_x, self.pos_y, self.restore_image = self.tile
        self.image = pygame.Surface(size, SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = self.pos_x
        self.rect.y = self.pos_y
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
        return WorldObject(self.tile, self.size, self.tile_id, self.fps, True, True, True)


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
        self.count_fps = 0

    def update(self):
        """play glowing animation"""
        length = len(self.animation) - 1

        if not self.spawned:
            self.image = self.animation[self.counter // 5]

            if self.counter is length * 5:
                self.spawned = True

            self.counter += 1
            self.dirty = 1
        else:
            self.count_fps = self.count_fps + 1 if self.count_fps < self.fps else 0
            '''pulsate the exit gate'''
            if (self.count_fps % self.fps) // 2 is 0 and self.count_fps is not 0:
                self.counter = length - 1 if self.counter is length else length
                self.image = self.animation[self.counter]
                self.dirty = 1
