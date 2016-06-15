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

    def __init__(self, surface, background):
        self.gravity = GRAVITY
        self.surface = surface
        self.background = background
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
        self.collide()

        playerGroup.clear(self.surface, self.background)
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

    def collide(self):
        """calculates collision for players and sprites"""
        # TODO: add head collide
        col = pygame.sprite.groupcollide(playerGroup, worldGroup, False, False)
        if len(col) > 0:
            # some collision
            for player in col.keys():
                for sprite in col[player]:
                    if sprite.climbable:
                        if player.change_x is not 0:
                            self.stop_horizontal_movement(player)
                        player.on_ladder = True
                    else:
                        # collision at feet
                        self.fix_pos(player, sprite)
                        """
                        else:
                          print("right %s" %sprite.rect.collidepoint(playerObj.rect.bottomright))
                          print("left %s" %sprite.rect.collidepoint(playerObj.rect.bottomleft))
                          print(sprite.rect.collidepoint(playerObj.rect.topright))
                          print(sprite.rect.collidepoint(playerObj.rect.topleft))"""
        else:
            for player in playerGroup:
                self.check_world_boundaries(player)
                player.on_ground = False
                player.on_ladder = False
                player.on_rope = False

        return col

    @staticmethod
    def stop_horizontal_movement(player):
        """stop left/right movement"""
        if player.change_x < 0:
            player.change_x += 0.1
        elif player.change_x > 0:
            player.change_x -= 0.1

    def fix_pos(self, player, sprite):
        """Used to place the player nicely"""
        # if player.rect.y > sprite.rect.y - player.rect.height:
        #    player.rect.y = sprite.rect.y - player.rect.height
        if sprite.solid:
            if player.rect.left is not sprite.rect.right or player.rect.right is not sprite.rect.left:
                    if player.change_y > 0:
                        '''player hits the ground'''
                        player.rect.bottom = sprite.rect.top
                        player.change_y = 0
                        player.on_ground = True
                    elif player.change_y < 0:
                        '''player hits sprite from below'''
                        player.rect.top = sprite.rect.bottom
                        self.stop_horizontal_movement(player)
            elif player.rect.bottom is not sprite.rect.top:
                if player.change_x > 0:
                    '''player hits the left side'''
                    player.rect.right = sprite.rect.left
                    player.change_x = 0
                elif player.change_x < 0:
                    '''player hits the right side'''
                    player.rect.left = sprite.rect.right
                    player.change_x = 0

    def get_level_info_json(self):
        pass

    def set_level_info_via_json(self, json):
        pass
    


class WorldObject(pygame.sprite.DirtySprite):
    """hello world"""

    def __init__(self, tile, solid=True, climbable=False, climbable_horizontal=False):
        """world object item"""
        (pos_x, pos_y, self.image) = tile
        pygame.sprite.DirtySprite.__init__(self, worldGroup)
        self.rect = self.image.get_rect()
        self.rect.x = pos_x * TILE_WIDTH
        self.rect.y = pos_y * TILE_HEIGHT
        self.solid = solid
        self.climbable = climbable
        self.climbable_horizontal = climbable_horizontal

    def update(self):
        """update world objects"""
        self.dirty = 1
