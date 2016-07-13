#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Collection of classes that are used as Level Sprites (Blocks, Ropes, Ladders, Gold etc)"""

from pygame.locals import *
from pyrunner_classes import logging, pygame, datetime
from pyrunner_classes.spritesheet_handling import SpriteSheet

log = logging.getLogger("World Objects")


class WorldObject(pygame.sprite.DirtySprite):
    """hello world"""

    group = pygame.sprite.LayeredDirty(default_layer=0)
    removed = pygame.sprite.LayeredDirty(default_layer=0)
    network_kill_list = []

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
        self.is_rope = False
        self.collectible = False
        self.killed = False
        self.restoring = restoring
        self.restore_change_x, self.restore_change_y = int(round(self.size[0] / 16)), int(round(self.size[1] / 16))
        self.change_coll_x, self.change_coll_y = int(round(self.size[0] / 8)), int(round(self.size[1] / 8))
        self.change_coll_w, self.change_coll_h = self.change_coll_x * 2, self.change_coll_y * 2
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
                y -= self.restore_change_x
                h += self.restore_change_y
            elif self.removable:
                y += self.restore_change_x
                h -= self.restore_change_y
            elif self.collectible:
                x += self.change_coll_x
                y += self.change_coll_y
                w -= self.change_coll_w
                h -= self.change_coll_h

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

    @staticmethod
    def get_removed_block_ids():
        ids = []
        for a in WorldObject.removed:
            ids.append(a.tile_id)

    @staticmethod
    def remove_blocks_by_ids(kill_list):
        for a in kill_list:
            kill_world_object(a)
        
        
    @staticmethod
    def kill_world_object(item_index):
        """kill a specific item in the WorldObject.group"""
        for index, world_object in enumerate(WorldObject.group, item_index):
            if world_object.index == item_index:
                world_object.kill()
                return

    def kill(self):
        """remove this sprite"""
        if self.removable or self.collectible:
            if not self.killed and self.removable:
                RemovedBlock(self.tile, self.rect.size, self.tile_id, self.fps, 10)
            self.killed = True
        else:
            '''let the network server know which sprite got killed'''
            WorldObject.network_kill_list.append(self.index)
            '''always update the indices'''
            self.update_indices()
            '''remove the tile from all groups'''
            self.super_kill()

    def super_kill(self):
        """call the parent class kill function"""
        self.dirty = 1
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
        self.is_rope = True


class Collectible(WorldObject):
    """collectible gold"""
    def __init__(self, tile, size, tile_id, fps):
        WorldObject.__init__(self, tile, size, tile_id, fps)
        self.collectible = True
        self.speed = (self.size[0] / 10) * 2
        self.change_y = 0
        self.got_dropped = True
        self.frame_counter = 0
        self.ground = None

    def update(self):
        """fall down to the ground"""
        if self.got_dropped:
            on_ground = False

            for tile in WorldObject.group:
                if tile != self:
                    if self.rect.collidepoint(tile.rect.centerx, tile.rect.top - self.change_coll_h):
                        on_ground = True
                        self.rect.bottom = tile.rect.top - self.change_coll_h
                        self.change_y = 0
                        self.ground = tile
                        log.debug("ground sprite = " + str(tile.rect) + " self: " + str(self.rect))
                        break

            if not on_ground:
                self.ground = None
                log.debug("falling down")
                '''increase the speed as fast as a player falls down'''
                if self.speed <= self.change_y <= self.speed * 2.5:
                    self.change_y += .35
                else:
                    self.change_y = self.speed

                self.rect.y += self.change_y
                self.dirty = 1
            else:
                if self.frame_counter >= self.fps * 2 and self.change_y is 0:
                    '''turn it off again if the bottom block got restored and the restore animation is over'''
                    self.got_dropped = False
                    self.frame_counter = 0
                    log.debug("stopping refresh")
                else:
                    self.rect.bottom = self.ground.rect.top - self.change_coll_h
                    self.frame_counter += 1
                    log.debug(str(self.rect.bottom) + " vs " + str(self.ground.rect.top))

        super(Collectible, self).update()


class RemovedBlock(pygame.sprite.DirtySprite):
    """store values of removed blocks to restore them later on"""
    def __init__(self, tile, size, tile_id, fps=25, time_out=1):
        pygame.sprite.DirtySprite.__init__(self, WorldObject.removed)
        self.tile = tile
        self.size = size
        self.tile_id = tile_id
        self.fps = fps
        self.time_out = time_out
        self.timer = datetime.now()
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
        if (datetime.now() - self.timer).seconds == self.time_out:
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
