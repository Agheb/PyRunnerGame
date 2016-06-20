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
        self.collide_rect()
        self.collide_ratio()
        # TODO: eventuell eine dritte collision funktion, die collisions mit der mitte der Sprites überprüft.

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

    def collide_rect(self):
        """calculates collision for players and sprites using the rectangles of the sprites"""
        col_rect = pygame.sprite.groupcollide(playerGroup, worldGroup, False, False)
        if len(col_rect) > 0:  # some collision
            for player in col_rect.keys():
                for sprite in col_rect[player]:

                    if sprite.climbable:
                        if player.change_x is not 0:
                            self.stop_horizontal_movement(player)
                        player.on_ladder = True
                        player.on_rope = False

                    elif sprite.collectible:
                        # TODO Gold Block enfernen, siehe WorldObjects
                        # (drüber zeichnen, aus spritegroup wird die gold instanz schon entfernt)
                        player.gold_count += 1
                        print(player.gold_count)
                        dirty_rect = self.background.subsurface(sprite)
                        self.surface.blit(dirty_rect, sprite)
                        WorldObject.kill(sprite)

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

        return col_rect

    def collide_ratio(self):
        """calculates collision for players and sprites using a extended ratio around the rectangles of the sprites"""
        col_ratio = pygame.sprite.groupcollide(playerGroup, worldGroup, False, False,
                                               collided=pygame.sprite.collide_rect_ratio(1.3))
        if len(col_ratio) > 0:  # some collision
            for player in col_ratio.keys():
                for sprite in col_ratio[player]:
                    # TODO Seitliche Kollision mi Seil soll Spieler nicht nach unten schieben
                    if sprite.climbable_horizontal:
                        if player.change_y is not 0:
                            self.stop_vertical_movement(player)
                            player.on_rope = True
                            player.on_ladder = False
                            player.on_ground = True  # on_ground has to be set true so player only moves at keypress
                            player.rect.top = sprite.rect.bottom
        else:
            for player in playerGroup:
                self.check_world_boundaries(player)
                player.on_ground = False
                player.on_ladder = False
                player.on_rope = False

        return col_ratio

    @staticmethod
    def stop_horizontal_movement(player):
        """stop left/right movement"""
        if player.change_x < 0:
            player.change_x += 0.1
        elif player.change_x > 0:
            player.change_x -= 0.1

    @staticmethod
    def stop_vertical_movement(player):
        """stop left/right movement"""
        if player.change_y < 0:
            player.change_y += 0.1
        elif player.change_y > 0:
            player.change_y -= 0.1

    def fix_pos(self, player, sprite):
        """Used to place the player nicely"""
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

    def __init__(self, tile=None, solid=True, climbable=False, climbable_horizontal=False, collectible=False):
        """world object item"""
        (pos_x, pos_y, self.image) = tile
        pygame.sprite.DirtySprite.__init__(self, worldGroup)
        self.rect = self.image.get_rect()
        self.rect.x = pos_x * TILE_WIDTH
        self.rect.y = pos_y * TILE_HEIGHT
        self.solid = solid
        self.climbable = climbable
        self.climbable_horizontal = climbable_horizontal
        self.collectible = collectible

    def update(self):
        """update world objects"""
        self.dirty = 1


class RemovableWorldObjects(WorldObject):  # TODO
    def __init__(self, spritesheet, tile=None, solid=True, climbable=False, climbable_horizontal=False,
                 collectible=False):
        (pos_x, pos_y, self.spritesheet) = tile
        self.spritesheet = spritesheet
        WorldObject(None, solid, climbable, climbable_horizontal, collectible)

    def remove_block(self, pos_x, pos_y):
        """remove the block passed in by the block_id parameter. it has to be deleted from the sprite.group"""
        WorldObject.remove(worldGroup)
        pass

    def add_removed_block(self, pos_x, pos_y):
        """add the block passed in by the block_id parameter. it has to be added to the sprite.group"""
        WorldObject.add(worldGroup)
        pass
