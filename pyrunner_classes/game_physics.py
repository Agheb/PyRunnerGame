#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python 2 related fixes
from __future__ import division
from .level import *
from .player import *
from .non_player_characters import Bots
import pygame
import logging
import pdb

log = logging.getLogger("Physics")


class Physics(object):
    """physics"""

    def __init__(self, level, screen):
        self.level = level
        self.surface = screen

        # TODO: set level id on level id, via level.py or WorldObjects

    def check_world_boundaries(self, player):
        """make sure the player stays on the screen"""
        '''player'''
        x, y, width, height = player.rect
        '''boundaries'''
        left = self.level.margin_left
        right = left + self.level.width - width
        top = self.level.margin_top
        bottom = top + self.level.height - height

        if y > bottom:
            player.rect.y = bottom
        elif y < top:
            player.rect.y = top
        if x > right:
            player.rect.x = right
        elif x < left:
            player.rect.x = left

    @staticmethod
    def find_collision(x, y, group=WorldObject.group):
        """find a sprite that has no direct collision with the player sprite"""
        for sprite in group:
            if sprite.rect.collidepoint(x, y):
                return sprite
        return None

    def check_collisions(self):
        """calculates collision for players and sprites using the rectangles of the sprites"""
        for player in Player.group:
            # check if the player is still on the screen
            self.check_world_boundaries(player)
            half_size = player.tile_size // 2

            # assume he's flying in the air
            on_rope = False
            on_ladder = False
            on_ground = False
            can_go_down = False

            '''important sprites for the bot'''
            bottom_sprite = self.find_collision(player.rect.centerx, player.rect.bottom + half_size)
            left_sprite = self.find_collision(player.rect.centerx - player.tile_size, player.rect.bottom + half_size)
            right_sprite = self.find_collision(player.rect.centerx + player.tile_size, player.rect.bottom + half_size)

            '''check if there's a ladder below the feet'''
            bot_go_down = True if bottom_sprite and bottom_sprite.climbable and not player.is_human else False
            no_bottom_left = False if left_sprite else True
            no_bottom_right = False if right_sprite else True
            on_tile = bottom_sprite.tile_id if bottom_sprite else None

            '''find collisions according to certain actions outside of the direct sprite collision'''
            if player.direction is "DR":
                '''remove the bottom sprite to the right'''
                if right_sprite and right_sprite.removable:
                    right_sprite.kill()
            elif player.direction is "DL":
                '''remove the bottom sprite to the left'''
                if left_sprite and left_sprite.removable:
                    left_sprite.kill()
            elif player.direction is "UD" and not player.on_ladder:
                '''go down the top part of a solid ladder'''
                if bottom_sprite and bottom_sprite.climbable or player.on_rope:
                    if player.change_y > 0:
                        # bottom_sprite.dirty = 1
                        can_go_down = True
                        player.rect.y += half_size
                        on_ladder = True
            else:
                '''make sure there's ground below the player'''
                if not bottom_sprite and not player.on_rope:
                    '''if there's no ground below the feet'''
                    on_ground = False
                    on_ladder = False
                    player.stop_on_ground = True

            '''find collisions with removed blocks'''
            removed_collision = self.find_collision(player.rect.centerx, player.rect.top, WorldObject.removed)
            if removed_collision:
                if not removed_collision.trapped and not player.is_human:
                    removed_collision.trapped = True
                    self.hit_inner_bottom(player, removed_collision)

            '''if a removed block contains another player we can walk over it'''
            top_collision = self.find_collision(player.rect.centerx, player.rect.bottom, Player.group)
            if top_collision:
                on_ground = True
                self.hit_top(player, top_collision)

            '''kill players touched by bots'''
            if player.is_human:
                killer = self.find_collision(player.rect.centerx, player.rect.centery, Player.group)
                if not killer.is_human:
                    player.kill()

            '''handle all other direct collisions'''
            collisions = pygame.sprite.spritecollide(player, WorldObject.group, False, False)
            for sprite in collisions:
                # sprite.dirty = 1
                # collect gold and remove the sprite
                if sprite.collectible and not sprite.killed:
                    if player.is_human:
                        '''only human players can take gold'''
                        player.add_gold()
                        # clear the item
                        # self.level.clean_sprite(sprite)
                        # and remove it
                        sprite.kill()
                elif sprite.exit:
                    if sprite.rect.left < player.rect.centerx < sprite.rect.right:
                        if not player.killed:
                            player.rect.center = sprite.rect.center
                            player.reached_exit = True
                            player.kill()
                elif sprite.restoring:
                    player.kill()
                elif sprite.rect.collidepoint(player.rect.center):
                    x, y = sprite.tile_id
                    """check which sprite contains the player"""
                    if sprite.climbable_horizontal and player.direction is not "Falling":
                        y += 1
                        """player is hanging on the rope"""
                        on_rope = True
                        player.rect.top = sprite.rect.top
                    elif sprite.climbable:
                        """player is climbing a ladder"""
                        on_ladder = True
                        if player.change_x is 0:
                            player.rect.centerx = sprite.rect.centerx
                        if player.change_y is 0:
                            player.rect.y = sprite.rect.y
                    on_tile = x, y
                elif sprite.rect.collidepoint(player.rect.midbottom) and not can_go_down:
                    """if the player hits a solid sprite at his feet"""
                    if sprite.solid and not sprite.climbable_horizontal:
                        on_ground = True
                        self.hit_top(player, sprite)
                elif not can_go_down:
                    self.fix_pos(player, sprite)

            # update the player variables
            player.on_tile = on_tile
            player.on_rope = on_rope
            player.on_ladder = on_ladder
            player.on_ground = on_ground
            player.can_go_down = can_go_down if player.is_human else bot_go_down
            # variables only relevant to the bot
            player.no_bottom_left = no_bottom_left
            player.no_bottom_right = no_bottom_right

    @staticmethod
    def hit_inner_bottom(player, sprite):
        """player hits the inner ground of a sprite"""
        if player.rect.bottom > sprite.rect.bottom:
            player.rect.center = sprite.rect.center
            player.change_x = 0
            player.change_y = 0
            player.on_ground = True
            player.direction = "Trapped"

    @staticmethod
    def hit_top(player, sprite):
        """player hits the ground"""
        if player.rect.bottom > sprite.rect.top:
            player.rect.bottom = sprite.rect.top + 1    # for permanent ground collision
            player.change_y = 0
            if player.change_x is 0:
                '''make sure the player stands in a correct position'''
                player.rect.centerx = sprite.rect.centerx

    @staticmethod
    def hit_bottom(player, sprite):
        """player hits higher level from below"""
        if player.rect.top < sprite.rect.bottom:
            player.rect.top = sprite.rect.bottom

    @staticmethod
    def hit_left(player, sprite):
        """player hits left side of a sprite"""
        if player.rect.right > sprite.rect.left:
            player.rect.right = sprite.rect.left
            player.change_x = 0

    @staticmethod
    def hit_right(player, sprite):
        """player hits right side of a sprite"""
        if player.rect.left < sprite.rect.right:
            player.rect.left = sprite.rect.right
            player.change_x = 0

    def fix_pos(self, player, sprite):
        """Used to place the player nicely"""

        if sprite.solid:
            if sprite.climbable and not player.on_ladder:
                if player.change_y > 0:
                    self.hit_top(player, sprite)
                elif player.change_y < 0:
                    self.hit_bottom(player, sprite)
            elif not sprite.climbable_horizontal:
                if sprite.rect.y < player.rect.y:
                    """ignore left/right collisions with sprites that are below the player"""
                    if player.change_x > 0:
                        self.hit_left(player, sprite)
                    elif player.change_x < 0:
                        self.hit_right(player, sprite)
