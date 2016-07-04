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

            '''find collisions with removed blocks'''
            removed_collision = self.find_collision(player.rect.centerx, player.rect.top, WorldObject.removed)
            if removed_collision:
                if not removed_collision.trapped:
                    '''only trap bots'''
                    if not player.is_human:
                        self.hit_inner_bottom(player, removed_collision)
                        removed_collision.trapped = True
                        on_ground = True

            if not player.is_human:
                '''add sprites left and right of the bot for collision detection'''
                right_tile = self.find_collision(player.rect.centerx + half_size, player.rect.y, WorldObject.group)
                if right_tile and not (right_tile.collectible or right_tile.climbable):
                    player.right_tile = right_tile
                else:
                    player.right_tile = None

                left_tile = self.find_collision(player.rect.centerx - half_size, player.rect.y, WorldObject.group)
                if left_tile and not (left_tile.collectible or left_tile.climbable):
                    player.left_tile = left_tile
                else:
                    player.left_tile = None

            '''important sprites for the bot'''
            bottom_sprite = self.find_collision(player.rect.centerx, player.rect.bottom + half_size)
            can_jump_off = True if not bottom_sprite or bottom_sprite.climbable else False

            '''check if there's a ladder below the feet'''
            bot_go_down = True if bottom_sprite and bottom_sprite.climbable and not player.is_human else False
            on_tile = bottom_sprite.tile_id if bottom_sprite else None

            '''find collisions according to certain actions outside of the direct sprite collision'''
            if player.direction is "DR":
                right_sprite = self.find_collision(player.rect.centerx + player.tile_size,
                                                   player.rect.bottom + half_size)
                '''remove the bottom sprite to the right'''
                if right_sprite and right_sprite.removable:
                    right_sprite.kill()
            elif player.direction is "DL":
                left_sprite = self.find_collision(player.rect.centerx - player.tile_size,
                                                  player.rect.bottom + half_size)
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

            '''if a removed block contains another player we can walk over it'''
            top_collision = self.find_collision(player.rect.centerx, player.rect.bottom, Player.group)
            if top_collision and top_collision.direction == "Trapped":
                on_ground = True
                '''if a bot hits a player from below the player should die'''
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
                    on_tile = sprite.tile_id
                    """check which sprite contains the player"""
                    if sprite.is_rope and player.direction is not "Falling":
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
                elif sprite.rect.collidepoint(player.rect.midbottom) and not can_go_down:
                    """if the player hits a solid sprite at his feet"""
                    if sprite.solid and not sprite.is_rope:
                        on_ground = True
                        self.hit_top(player, sprite)
                elif not can_go_down and sprite is not bottom_sprite:
                    self.fix_pos(player, sprite)

            # update the player variables
            player.on_tile = on_tile
            player.on_rope = on_rope
            player.can_jump_off = can_jump_off
            player.on_ladder = on_ladder
            player.on_ground = on_ground
            player.can_go_down = can_go_down if player.is_human else bot_go_down

    @staticmethod
    def hit_inner_bottom(player, sprite):
        """player hits the inner ground of a sprite"""
        if player.rect.bottom > sprite.rect.bottom - 1 and not player.is_human:
            player.direction = "Trapped"
            player.change_x = 0
            player.change_y = 0
            player.rect.midbottom = sprite.rect.midbottom

    @staticmethod
    def hit_top(player, sprite):
        """player hits the ground"""
        if player.rect.bottom > sprite.rect.top:
            top = sprite.rect.top
            # the player collides with sprites left and right in the ground of a trapped player
            if not isinstance(sprite, Player):
                # so we can only add one on regular sprites for permanent ground collision
                # if we don't add one the player will lose ground contact every frame and think he falls
                top += 1
            player.rect.bottom = top
            player.change_y = 0
            if player.change_x is 0:
                '''make sure the player stands in a correct position'''
                player.rect.centerx = sprite.rect.centerx

    @staticmethod
    def hit_bottom(player, sprite):
        """player hits higher level from below"""
        if player.rect.top < sprite.rect.bottom:
            player.rect.top = sprite.rect.bottom + 1

    @staticmethod
    def hit_left(player, sprite):
        """player hits left side of a sprite"""
        if player.rect.right > sprite.rect.left and player.rect.centery >= sprite.rect.y:
            player.rect.right = sprite.rect.left
            player.change_x = 0

    @staticmethod
    def hit_right(player, sprite):
        """player hits right side of a sprite"""
        if player.rect.left < sprite.rect.right and player.rect.centery >= sprite.rect.y:
            player.rect.left = sprite.rect.right
            player.change_x = 0

    def fix_pos(self, player, sprite):
        """Used to place the player nicely"""
        if sprite.solid:
            if sprite.climbable:
                if not player.on_ladder:
                    if player.change_y > 0:
                        self.hit_top(player, sprite)
                    elif player.change_y < 0:
                        self.hit_bottom(player, sprite)
            elif not player.on_rope and not sprite.collectible and not sprite.is_rope:
                """ignore left/right collisions with sprites that are below the player"""
                if player.change_x > 0:
                    self.hit_left(player, sprite)
                elif player.change_x < 0:
                    self.hit_right(player, sprite)
