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
        self.player_2 = None  # Player(self.level.player_2_pos, "LRCharacters32_p2.png")

        return

    def update(self):
        """updates all physics components"""
        # pass all changed sprites to the render thread
        rects = []

        Player.group.update()
        WorldObject.group.update()

        # check for collisions
        self.collide_rect()

        rects.append(Player.group.draw(self.surface))
        rects.append(WorldObject.group.draw(self.surface))

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

    @staticmethod
    def find_collision(x, y):
        """find a sprite that has no direct collision with the player sprite"""
        for sprite in WorldObject.group:
            if sprite.rect.collidepoint(x, y):
                return sprite
        return None

    def collide_rect(self):
        """calculates collision for players and sprites using the rectangles of the sprites"""
        for player in Player.group:
            # check if the player is still on the screen
            self.check_world_boundaries(player)

            # assume he's flying in the air
            on_rope = False
            on_ladder = False
            on_ground = False
            go_down = False

            '''find collisions according to certain actions outside of the direct sprite collision'''
            if player.direction is "DR":
                '''remove the bottom sprite to the right'''
                right_sprite = self.find_collision(player.rect.centerx + player.tile_size, player.rect.bottom + 1)

                if right_sprite and right_sprite.removable:
                    self.level.clean_sprite(right_sprite)
                    right_sprite.kill()
            elif player.direction is "DL":
                '''remove the bottom sprite to the left'''
                left_sprite = self.find_collision(player.rect.centerx - player.tile_size, player.rect.bottom + 1)

                if left_sprite and left_sprite.removable:
                    self.level.clean_sprite(left_sprite)
                    left_sprite.kill()
            elif player.direction is "UD" and not player.on_ladder:
                '''go down the top part of a solid ladder'''
                bottom_sprite = self.find_collision(player.rect.centerx, player.rect.bottom + 1)

                if bottom_sprite and bottom_sprite.climbable and player.change_y > 0:
                    player.on_ladder = True
                    go_down = True
            else:
                '''make sure there's ground below the player'''
                bottom_sprite = self.find_collision(player.rect.centerx, player.rect.bottom + 1)

                if not bottom_sprite and not player.on_rope:
                    '''if there's no ground below the feet'''
                    player.schedule_stop()
                    on_ground = False

            '''handle all other direct collisions'''
            collisions = pygame.sprite.spritecollide(player, WorldObject.group, False, False)
            for sprite in collisions:
                # collect gold and remove the sprite
                if sprite.collectible and not sprite.killed:
                    player.gold_count += 1
                    print(player.gold_count)
                    # clear the item
                    self.level.clean_sprite(sprite)
                    # and remove it
                    sprite.kill()
                elif sprite.rect.collidepoint(player.rect.center):
                    """check which sprite contains the player"""
                    if sprite.climbable_horizontal and player.direction is not "UD":
                        """player is hanging on the rope"""
                        on_rope = True
                        player.rect.top = sprite.rect.top
                    elif sprite.climbable:
                        """player is climbing a ladder"""
                        on_ladder = True
                elif sprite.rect.collidepoint(player.rect.midbottom):
                    """if the player hits a solid sprite at his feet"""
                    if sprite.solid and not sprite.climbable_horizontal and not go_down:
                        on_ground = True
                        self.hit_top(player, sprite)
                else:
                    self.fix_pos(player, sprite)

            # update the player variables
            player.on_rope = on_rope
            player.on_ladder = on_ladder
            player.on_ground = on_ground

    @staticmethod
    def hit_top(player, sprite):
        """player hits the ground"""
        if player.rect.bottom > sprite.rect.top:
            player.rect.bottom = sprite.rect.top + 1    # for permanent ground collision
            player.change_y = 0

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

    def get_level_info_json(self):
        pass

    def set_level_info_via_json(self, json):
        pass
