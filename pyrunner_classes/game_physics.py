#!/usr/bin/python
# -*- coding: utf-8 -*-
"""class that handles all sprite collisions"""
from pyrunner_classes import logging, pygame
from pyrunner_classes.player import Player
from pyrunner_classes.level_objecs import WorldObject

log = logging.getLogger("Physics")


class Physics(object):
    """physics"""

    def __init__(self, level):
        self.level = level
        '''sounds'''
        self.sfx_coin_collected = pygame.mixer.Sound(self.level.sound_thread.get_full_path_sfx('player_collect.wav'))
        self.sfx_coin_robbed = pygame.mixer.Sound(self.level.sound_thread.get_full_path_sfx('Robbed_Point_01.wav'))
        self.sfx_player_portal = pygame.mixer.Sound(self.level.sound_thread.get_full_path_sfx('portal_exit.wav'))
        self.sfx_player_killed = pygame.mixer.Sound(self.level.sound_thread.get_full_path_sfx('player_kill.ogg'))
        self.sfx_player_dig = pygame.mixer.Sound(self.level.sound_thread.get_full_path_sfx('sfx_sounds_interaction24.wav'))

    def register_callback(self, network):
        """creates a link to the network connector, this is needed to notify the network of canged blocks"""
        self.level.network_connector = network

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

    @staticmethod
    def remove_sprites_by_id(sprite_ids):
        """remove a specific sprite"""
        log.info("removing sprites")
        for sprite in WorldObject.group:
            if sprite.tile_id in sprite_ids:
                sprite.kill()
    
    def check_collisions(self):
        """calculates collision for players and sprites using the rectangles of the sprites"""
        for player in Player.group:
            # check if the player is still on the screen
            self.check_world_boundaries(player)
            half_size = player.size / 2

            # assume he's flying in the air
            on_rope = False
            on_ladder = False
            on_ground = False
            can_go_down = False

            '''kill players touched by bots'''
            if not player.is_human and not player.direction == "Trapped":
                human_victims = pygame.sprite.spritecollide(player, Player.humans, False,
                                                            collided=pygame.sprite.collide_rect_ratio(0.5))
                if human_victims:
                    for p in human_victims:
                        if not p.killed:
                            self.level.sound_thread.play_sound(self.sfx_player_killed)
                            p.kill()

            '''find collisions with removed blocks'''
            removed_collision = self.find_collision(player.rect.centerx, player.rect.top, WorldObject.removed)
            if removed_collision:
                if not removed_collision.trapped:
                    '''only trap bots'''
                    if not player.is_human:
                        self.hit_inner_bottom(player, removed_collision)
                        removed_collision.trapped = True
                        on_ground = True

            '''add sprites left and right of the bot for collision detection'''
            right_tile = self.find_collision(player.rect.right + half_size, player.rect.centery, WorldObject.group)
            right_bottom = self.find_collision(player.rect.right + half_size, player.rect.bottom + half_size)
            '''find sprites to the left'''
            left_tile = self.find_collision(player.rect.left - half_size, player.rect.centery, WorldObject.group)
            left_bottom = self.find_collision(player.rect.left - half_size, player.rect.bottom + half_size)

            if not player.is_human:
                if right_tile and not right_tile.collectible and not right_tile.climbable:
                    player.right_tile = right_tile
                else:
                    player.right_tile = None

                player.right_bottom = right_bottom if right_bottom else None

                if left_tile and not left_tile.collectible and not left_tile.climbable:
                    player.left_tile = left_tile
                else:
                    player.left_tile = None

                player.left_bottom = left_bottom if left_bottom else None

            '''important sprites for the bot'''
            bottom_sprite = self.find_collision(player.rect.centerx, player.rect.bottom + half_size)
            can_jump_off = True if not bottom_sprite or bottom_sprite.climbable else False

            '''check if there's a ladder below the feet'''
            bot_go_down = True if bottom_sprite and bottom_sprite.climbable and not player.is_human else False
            on_tile = bottom_sprite.tile_id if bottom_sprite else None

            '''find collisions according to certain actions outside of the direct sprite collision'''
            if player.direction is "DR":
                '''remove the bottom sprite to the right'''
                if right_bottom and right_bottom.removable and not right_tile:
                    right_bottom.kill()
                    self.level.sound_thread.play_sound(self.sfx_player_dig)
            elif player.direction is "DL":
                '''remove the bottom sprite to the left'''
                if left_bottom and left_bottom.removable and not left_tile:
                    left_bottom.kill()
                    self.level.sound_thread.play_sound(self.sfx_player_dig)
            elif player.direction is "UD" and not player.on_ladder:
                '''go down the top part of a solid ladder'''
                if bottom_sprite and bottom_sprite.climbable or player.on_rope:
                    if player.change_y > 0:
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

            '''handle all other direct collisions'''
            collisions = pygame.sprite.spritecollide(player, WorldObject.group, False, False)
            for sprite in collisions:
                # sprite.dirty = 1
                # collect gold and remove the sprite
                if sprite.collectible and not sprite.killed:
                    if player.is_human:
                        '''only human players can take gold'''
                        player.add_gold()
                        "Collect gold SFX"
                        self.level.sound_thread.play_sound(self.sfx_coin_collected)
                        '''notify the server'''
                        self.level.network_connector.client.gold_removed(sprite.tile_id)
                        # remove it
                        sprite.kill()
                    elif not player.robbed_gold:
                        player.collect_gold(sprite)
                        # play sound when collecting gold
                        self.level.sound_thread.play_sound(self.sfx_coin_robbed)
                elif sprite.exit:
                    if sprite.rect.left < player.rect.centerx < sprite.rect.right:
                        if not player.killed:
                            player.rect.center = sprite.rect.center
                            if player.is_human:
                                self.level.reached_next_level = True
                                player.reached_exit = True  # keep his gold coins
                            # Play Exit sound
                            self.level.sound_thread.play_sound(self.sfx_player_portal)
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
        if player.rect.bottom >= sprite.rect.bottom and not player.is_human:
            player.direction = "Trapped"
            player.change_x = 0
            player.change_y = 0
            player.rect.center = sprite.rect.center

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
        if player.rect.right > sprite.rect.left and player.rect.centery > sprite.rect.y:
            player.rect.right = sprite.rect.left
            player.change_x = 0

    @staticmethod
    def hit_right(player, sprite):
        """player hits right side of a sprite"""
        if player.rect.left < sprite.rect.right and player.rect.centery > sprite.rect.y:
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
