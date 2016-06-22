#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python 2 related fixes
from __future__ import division
from .player import *
import pygame

GRAVITY = 1
MULTIPLICATOR = 1
TILE_WIDTH = 32
TILE_HEIGHT = 32

worldGroup = pygame.sprite.LayeredDirty()
playerGroup = pygame.sprite.LayeredDirty()


class Physics(object):
    """physics"""

    def __init__(self, surface, level):
        self.gravity = GRAVITY
        self.surface = surface
        self.lvl_surface = level.surface
        self.background = level.background
        self.player = Player()
        playerGroup.add(self.player)
        return

    def update(self):
        """updates all physics components"""
        # TODO: pass sprites to render thread
        rects = []
        rects.append(playerGroup.draw(self.surface))
        rects.append(worldGroup.draw(self.surface))

        playerGroup.update()

        self.collide_rect()
        # TODO: eventuell eine dritte collision funktion, die collisions mit der mitte der Sprites überprüft.

        playerGroup.clear(self.surface, self.lvl_surface)
        worldGroup.clear(self.surface, self.background)
        return rects

    def check_world_boundaries(self, player):
        """make sure the player stays on the screen"""
        width, height = self.surface.get_size()
        width -= TILE_WIDTH
        height -= TILE_HEIGHT

        if player.rect.y > height:
            player.rect.y = height
        elif player.rect.y < 0:
            player.rect.y = 0
        if player.rect.x > width:
            player.rect.x = width
        elif player.rect.x < 0:
            player.rect.x = 0

    def collide_rect(self):
        """calculates collision for players and sprites using the rectangles of the sprites"""
        col_rect = pygame.sprite.groupcollide(playerGroup, worldGroup, False, False)

        for player in playerGroup:
            # check if the player is still on the screen
            self.check_world_boundaries(player)

            if player not in col_rect.keys():
                player.on_ladder = False
                player.on_rope = False
                player.on_ground = False
            else:
                for sprite in col_rect[player]:
                    if sprite.climbable and player.change_x is 0:
                        player.on_ladder = True
                        player.on_rope = False
                    elif sprite.climbable_horizontal and player.change_y is 0:
                        player.on_rope = True
                        player.on_ladder = False
                    elif sprite.collectible:
                        player.gold_count += 1
                        print(player.gold_count)
                        # clear the item
                        dirty_rect = self.background.subsurface(sprite.rect)
                        self.surface.blit(dirty_rect, sprite.rect)
                        self.lvl_surface.blit(dirty_rect, sprite.rect)
                        # sprite.dirty = 1
                        sprite.kill()
                    else:
                        # collision at feet
                        self.fix_pos(player, sprite)

        return col_rect

    @staticmethod
    def fix_pos(player, sprite):
        """Used to place the player nicely"""
        if sprite.solid:
            if not sprite.climbable_horizontal:
                if player.change_y >= 0:
                    if player.rect.bottom > sprite.rect.top + 1:
                        '''player hits the ground'''
                        player.rect.bottom = sprite.rect.top + 1
                        player.change_y = 0
                        player.on_ground = True
                elif player.change_y < 0:
                    if player.rect.top < sprite.rect.bottom:
                        '''player hits sprite from below'''
                        player.rect.top = sprite.rect.bottom + 5
                        player.on_ground = False
            elif player.on_ladder:
                if player.change_x > 0:
                    if player.rect.right > sprite.rect.left:
                        '''player hits the left side'''
                        player.rect.right = sprite.rect.left
                        player.change_x = 0
                elif player.change_x < 0:
                    if player.rect.left < sprite.rect.right:
                        '''player hits the right side'''
                        player.rect.left = sprite.rect.right
                        player.change_x = 0

    def get_level_info_json(self):
        pass

    def set_level_info_via_json(self, json):
        pass


class WorldObject(pygame.sprite.DirtySprite):
    """hello world"""

    def __init__(self, tile=None, solid=True):
        """world object item"""
        (pos_x, pos_y, self.image) = tile
        pygame.sprite.DirtySprite.__init__(self, worldGroup)
        self.rect = self.image.get_rect()
        self.rect.x = pos_x * TILE_WIDTH
        self.rect.y = pos_y * TILE_HEIGHT
        self.solid = solid
        self.climbable = False
        self.climbable_horizontal = False
        self.collectible = False

    def update(self):
        """update world objects"""
        self.dirty = 1


class Ladder(WorldObject):

    def __init__(self, tile):
        WorldObject.__init__(self, tile, False)
        self.climbable = True
        self.solid = False


class Rope(WorldObject):

    def __init__(self, tile):
        WorldObject.__init__(self, tile)
        self.climbable_horizontal = True


class Collectible(WorldObject):

    def __init__(self, tile):
        WorldObject.__init__(self, tile)
        self.collectible = True
