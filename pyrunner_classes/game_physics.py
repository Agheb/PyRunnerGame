#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python 2 related fixes
from __future__ import division
from .level import *
from .player import *
import pygame

GRAVITY = 1


class Physics(object):
    """physics"""

    def __init__(self, surface, level):
        self.gravity = GRAVITY
        self.surface = surface
        self.level = level
        self.lvl_surface = self.level.surface
        self.background = self.level.background
        self.player_1 = Player(self.level.player_1_pos, "LRCharacters32.png")
        self.player_2 = Player(self.level.player_2_pos, "LRCharacters32_p2.png")

        return

    def update(self):
        """updates all physics components"""
        # pass all changed sprites to the render thread
        rects = []
        rects.append(Player.group.draw(self.surface))
        rects.append(WorldObject.group.draw(self.surface))

        Player.group.update()
        # WorldObject.group.update()
        # check for collisions
        self.collide_rect()
        # clean up the dirty background
        Player.group.clear(self.surface, self.lvl_surface)
        WorldObject.group.clear(self.surface, self.background)
        # return the changed items
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
        for player in Player.group:
            # check if the player is still on the screen
            self.check_world_boundaries(player)

            # assume the player is floating in the air
            on_ladder = False
            on_rope = False
            on_ground = False

            for sprite in pygame.sprite.spritecollide(player, WorldObject.group, False, False):
                if sprite.climbable:
                    on_ladder = True
                elif sprite.climbable_horizontal:
                    on_rope = True
                elif sprite.solid:
                    on_ground = True
                # collect gold and remove the sprite
                if sprite.collectible:
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

            # update the players properties
            player.on_ladder = on_ladder
            player.on_rope = on_rope
            player.on_ground = on_ground

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
                        player.on_ladder = False
                elif player.change_y < 0 and not player.on_ladder:
                    if player.rect.top < sprite.rect.bottom:
                        '''player hits sprite from below'''
                        player.rect.top = sprite.rect.bottom + 5
                        player.on_ground = False
            elif player.on_ladder:
                if player.change_x > 0:
                    if player.rect.right > sprite.rect.left:
                        '''player hits the left side'''
                        player.rect.right = sprite.rect.left - 1
                        player.change_x = 0
                elif player.change_x < 0:
                    if player.rect.left < sprite.rect.right:
                        '''player hits the right side'''
                        player.rect.left = sprite.rect.right + 1
                        player.change_x = 0

    def get_level_info_json(self):
        pass

    def set_level_info_via_json(self, json):
        pass
