#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main pyRunner class which initializes all sub classes and threads"""
# Python 2 related fixes
from __future__ import division
import pytmx
from pytmx.util_pygame import load_pygame

from .game_physics import Physics
from .level_objecs import *
from .player import Player, GoldScore
from .non_player_characters import Bots
import pdb
from operator import itemgetter
from .dijkstra import Graph
import logging

log = logging.getLogger("Level")
LEVEL_PATH = "./resources/levels/"
LEVEL_EXT = ".tmx"

"""
Level Builder for PyRunner game
PyTMX is used to load tilemap into game
Level-Editor: Tiled
TMX ( Tiled Map XML) to describe a map
TMX- Specification:
"""


class Level(object):
    """
    Level object loads tmx-file for game and draws each tile to screen
    filename: Tilesheet and TMX-File must be in same folder
    1. Read in and parse TMX file
    2. load all tilesheet image
    3. draw layer by layer
    """
    PLAYERS = ["LRCharacters32_p1.png", "LRCharacters32_p2.png", "LRCharacters32_p3.png", "LRCharacters32_p4.png"]
    SM_SIZE = 32

    levels = []
    players = []
    bots = []

    def __init__(self, surface, path, sound_thread, network_connector, fps=25):
        self.surface = surface
        self.background = self.surface.copy()
        self.path = path
        self.sound_thread = sound_thread
        self.network_connector = network_connector
        self.fps = fps
        self.physics = Physics(self)
        self.graph = None
        self.climbable_list = []
        self.walkable_list = []
        self.bots_respawn = []
        self.bot_count = 0
        self.fps_counter = 0
        self.tm = load_pygame(self.path, pixelalpha=True)
        self.tile_width, self.tile_height = self.tm.tilewidth, self.tm.tileheight
        '''
            we have 32x32 pixel tiles and 40x23 pixels resulting in a resolution of 1280x736
            because we want 720p (1280x720) and 16:9 we have to get rid of half of the pixels in the last row
        '''
        self.cols = self.tm.width
        self.rows = self.tm.height
        tm_width = self.cols * self.tile_width
        tm_height = self.rows * self.tile_height - 16
        self.width, self.height = tm_width, tm_height
        self.pixel_diff = 0
        self.margin_left = 0
        self.margin_top = 0
        s_width, s_height = surface.get_size()

        if path not in Level.levels:
            Level.levels.append(path)

        if tm_height != s_height or tm_width != s_width:
            '''automatically scale the tilemap'''
            diff_h = (s_height - tm_height) // self.tm.height
            diff_w = (s_width - tm_width) // self.tm.width

            self.pixel_diff = diff_h if diff_h < diff_w else diff_w
            self.tile_width += self.pixel_diff
            self.tile_height += self.pixel_diff
            self.width = self.cols * self.tile_width
            self.height = self.rows * self.tile_height
            self.margin_left = (s_width - self.width) // 2
            self.margin_top = (s_height - self.height) // 2

        self.last_row = self.margin_top + self.height - self.tile_height

        try:
            p1_obj = self.tm.get_object_by_name("Player_1")
            p1_pos = self.calc_object_pos((p1_obj.x, p1_obj.y))
        except ValueError:
            p1_pos = 0, 0
        try:
            p2_obj = self.tm.get_object_by_name("Player_2")
            p2_pos = self.calc_object_pos((p2_obj.x, p2_obj.y))
        except ValueError:
            x, y = p1_pos
            p2_pos = x + 32, y
        try:
            bot1_obj = self.tm.get_object_by_name("Enemies_1")
            bot1_pos = self.calc_object_pos((bot1_obj.x, bot1_obj.y))
            self.bot_count += int(bot1_obj.type) if bot1_obj.type else 1
        except ValueError:
            '''enemies fall from the sky'''
            bot1_pos = (self.width - 100, 0)  # randint(0, self.width), 0

        try:
            bot2_obj = self.tm.get_object_by_name("Enemies_2")
            bot2_pos = self.calc_object_pos((bot2_obj.x, bot2_obj.y))
            self.bot_count += int(bot2_obj.type) if bot2_obj.type else 1
        except ValueError:
            '''enemies fall from the sky'''
            bot2_pos = (self.width - 100, 0)  # randint(0, self.width), 0
        try:
            next_level = self.tm.get_object_by_name("Exit_Gate")
            self.next_level_pos = self.calc_object_pos((next_level.x, next_level.y))
            self.next_level = LEVEL_PATH + next_level.type + LEVEL_EXT
        except ValueError:
            pass

        self.spawn_player_1_pos = p1_pos
        self.spawn_player_2_pos = p2_pos
        self.spawn_enemies_1_pos = bot1_pos
        self.spawn_enemies_2_pos = bot2_pos

        '''draw the complete level'''
        self.render()

        '''calculate walking paths'''
        self.generate_paths()

        '''add players'''
        self.spawn_bots()
        self.add_network_players()

    def update(self):
        """update level related things"""
        '''update all world sprites'''
        WorldObject.group.update()
        WorldObject.removed.update()

        '''draw the level'''
        rects = WorldObject.group.draw(self.surface)

        '''check for sprite collisions'''
        self.physics.check_collisions()

        '''check if there are bots to respawn'''
        self.check_respawn_bot()

        return rects

    def clear(self, screen):
        """clear the sprite backgrounds, call this after blitting the level surface to the screen"""
        Player.group.clear(screen, self.surface)
        GoldScore.scores.clear(screen, self.surface)
        WorldObject.group.clear(self.surface, self.background)
        # WorldObject.removed.clear(self.surface, self.background)

    def check_respawn_bot(self):
        """respawn a bot after a specified amount of time"""
        if self.fps_counter < self.fps:
            self.fps_counter += 1
        else:
            self.fps_counter = 0

            '''only check once per second if there are bots to respawn'''
            if self.bots_respawn:
                for bid, time in self.bots_respawn:
                    if (datetime.now() - time).seconds >= 10:
                        self.bots_respawn.remove((bid, time))
                        pos = self.spawn_enemies_1_pos if bid & 1 else self.spawn_enemies_2_pos
                        self.create_bot(bid, pos)

    def spawn_bots(self):
        """spawn the specified amount of bots in the level"""
        for i in range(self.bot_count):
            x, y = self.spawn_enemies_1_pos if i & 1 else self.spawn_enemies_2_pos
            '''create as many bots as specified in Object Type field'''
            x += self.tile_width * i
            self.create_bot(i, (x, y))

    def create_bot(self, bid, location):
        """create a bot at location (x, y)"""
        bot = Bots(bid, location, self.PLAYERS[bid % len(self.PLAYERS)], self)
        Level.bots.append(bot)

    def calc_object_pos(self, pos_pixel):
        """adjust pixels to scaled tile map"""
        x, y = pos_pixel
        x //= self.tm.tilewidth
        y //= self.tm.tileheight
        x *= self.tile_width
        y *= self.tile_height
        x += self.margin_left
        y += self.margin_top

        return x, y

    def render(self):
        """Create the level. Iterates through the layers in the TMX (see game_physics WorldObjects).
         For each Objects the properties are set as follows with defaults:
         (self, tile, solid=True, climbable=False, climbable_horizontal=False)
         """
        def check_property(current_layer, sprite_property):
            """check layer for a specific property and if it exists create the corresponding object"""
            try:
                if current_layer.properties[sprite_property] == 'true':
                    return True
                else:
                    return False
            except KeyError:
                return False

        def resize_tile_to_fit(tile, target_size):
            """resize tile to fit the screen size and position"""
            pos_x, pos_y, image = tile
            pos_id = pos_x, pos_y

            pos_x = self.margin_left + (width * pos_x)
            pos_y = self.margin_top + (height * pos_y)

            image = pygame.transform.scale(image, target_size)

            '''chop off the bottom half in the last row to fit 720p'''
            if pos_y == self.last_row:
                image = self.squeeze_half_image(image)

            tile = pos_x, pos_y, image

            return tile, pos_id

        width, height = self.tile_width, self.tile_height
        size = width, height

        for layer in self.tm.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                if layer.name == "Background":
                    for a in layer.tiles():
                        a, tile_id = resize_tile_to_fit(a, size)

                        '''create a blank copy of the background layer'''
                        self.render_tile(self.background, a)
                        self.render_tile(self.surface, a)
                else:
                    '''first check all layer properties'''
                    ladder = check_property(layer, 'climbable')
                    rope = check_property(layer, 'rope')
                    gold = check_property(layer, 'collectible')
                    removable = check_property(layer, 'removable')
                    solid = check_property(layer, 'solid')
                    wall = check_property(layer, 'vertical_wall')
                    width, height = self.tile_width, self.tile_height
                    fps = self.fps
                    '''create the sprites'''
                    for a in layer.tiles():
                        a, tile_id = resize_tile_to_fit(a, size)

                        if ladder:
                            Ladder(a, size, tile_id, fps, solid)
                        elif rope:
                            Rope(a, size, tile_id, fps)
                        elif gold:
                            Collectible(a, size, tile_id, fps)
                        elif removable:
                            WorldObject(a, size, tile_id, fps, solid, removable)
                        elif solid or wall:
                            WorldObject(a, size, tile_id, fps, solid)

                        if not gold and not wall:
                            '''
                                add all tiles that a player can walk on to this list
                                to generate paths for the shortest path algorithm
                            '''
                            x, y = tile_id
                            # ignore the last row because it gets cut by 16 pixels
                            if y is not self.rows - 1:
                                '''only add walkable tiles'''
                                if ladder:
                                    '''add ladders separately'''
                                    self.climbable_list.append(tile_id)
                                self.walkable_list.append(tile_id)

    def generate_paths(self):
        """create paths by id for bots"""
        # graph to use with dijkstra's shortest path algorithm
        self.graph = Graph()
        # remove duplicate entries (e.g. ropes that count one row deeper)
        self.walkable_list = list(set(self.walkable_list))
        # sort list by x, then by y
        self.walkable_list.sort(key=itemgetter(0))
        self.walkable_list.sort(key=itemgetter(1))

        horizontals = self.add_paths(self.walkable_list, True)    # horizontals =

        '''find all ladders'''
        # remove duplicate entries
        self.climbable_list = list(set(self.climbable_list))
        # sort list by x, then by y
        self.climbable_list.sort()

        '''add the bottom below the ladder as well'''
        ladder_plus = [tile_id for tile_id in self.climbable_list]
        old_y = 0
        for tile_id in self.climbable_list:
            x, y = tile_id
            if not old_y:
                old_y = y
            elif y is not old_y:
                ladder_plus.append((x, y + 1))
                old_y = y

        # remove duplicate entries
        ladders = list(set(ladder_plus))
        # sort list by x, then by y
        ladders.sort()

        self.add_paths(ladders, False)

        # '''initialize the graph'''
        # for tile_a in self.walkable_list:
        #     for tile_b in self.walkable_list:
        #         if tile_a is not tile_b:
        #             try:
        #                 self.graph.shortest_path(tile_a, tile_b)
        #                 # log.info("Success: %s and %s" % (tile_a, tile_b))
        #             except KeyError:
        #                 # log.info("Error %s and %s" % (tile_a, tile_b))
        #                 pass
        #
        # intersections = [tile_id for tile_id in horizontals if tile_id in ladders]
        # intersections.sort()
        #
        # '''partially initialize the graph'''
        # for tile in self.walkable_list:
        #     for ladder in intersections:
        #         if tile is not ladder:
        #             try:
        #                 self.graph.shortest_path(tile, ladder)
        #                 log.info("Success: %s and %s" % (tile, ladder))
        #             except KeyError:
        #                 # log.info("Error %s and %s" % (tile, ladder))
        #                 pass

    def get_is_path(self, a, b):
        """returns if a target is reachable"""
        try:
            return True if self.graph.shortest_path(a, b) else False
        except KeyError:
            return False

    def add_intersections(self, horizontals, intersections):
        """find all important intersections between layers and connect them"""
        for ladder_id in intersections:
            for tile_id in horizontals:
                if self.get_is_path(tile_id, ladder_id):
                    x, y = tile_id
                    lx, ly = ladder_id
                    length = x - lx if x > lx else lx - x
                    length += 1
                    self.graph.add_edge(tile_id, ladder_id, length)

    def add_long_path(self, cur_start, cur_stop, cur_locked_x_y, horizontal, tuple_list):
        """add a path that is longer than 1 tile"""
        length = cur_stop - cur_start
        if length:
            length += 1
            if horizontal:
                '''the length is + 1 because tiles start with index 0'''
                start_a, start_b = cur_start, cur_locked_x_y
                stop_a, stop_b = cur_stop, cur_locked_x_y
            else:
                '''connect the ladder to the next bottom horizontal row'''
                start_a, start_b = cur_locked_x_y, cur_start
                stop_a, stop_b = cur_locked_x_y, cur_stop
                tuple_list.append((stop_a, stop_b))
            '''name the nodes'''
            start_node = start_a, start_b
            stop_node = stop_a, stop_b
            '''add the edges'''
            self.graph.add_edge(start_node, stop_node, length)
            self.graph.add_edge(stop_node, start_node, length)
            log.info("adding path from %(start_node)s to %(stop_node)s with a length of %(length)s" % locals())

            # for node_a in range(stop_a, stop_b):
            #         for node_b in range(stop_a, stop_b):
            #             if node_a is not node_b:
            #                 length = node_b - node_a if node_b > node_a else node_a - node_b
            #                 length += 1
            #                 self.graph.add_edge(node_a, node_b, length)
            #                 # self.graph.add_edge(stop_node, start_node, length)
            #                 log.info("adding path from %(node_a)s to %(node_b)s with a length of %(length)s" % locals())

    def add_paths(self, node_list, horizontal=True):
        """find intersections between different levels"""

        def add_node(cur_x, cur_y, cur_x_y):
            """add a node and a short path between two neighboring tiles"""
            tuple_list.append((cur_x, cur_y))
            node = (cur_x, cur_y)
            self.graph.add_node(node)
            '''if it's not the first tile in a row or column add a path to the previous one'''
            if cur_x_y is not 0:
                prev_x, prev_y = (cur_x - 1, cur_y) if horizontal else (cur_x, cur_y - 1)
                prev_node = (prev_x, prev_y)
                self.graph.add_edge(node, prev_node, 1)
                self.graph.add_edge(prev_node, node, 1)

        '''variables to store the start and stop in a path'''
        tuple_list = []
        start = 0
        stop = 0
        locked_x_y = 0
        not_set = True

        for x, y in node_list:
            '''jump to the next item if this is the first'''
            if not_set:
                start = stop = x if horizontal else y
                locked_x_y = y if horizontal else x
                not_set = False
                continue

            '''make this function universal for horizontal and vertical lookups'''
            current_x_y = x if horizontal else y
            cur_row_col = y if horizontal else x

            if current_x_y == stop + 1 and locked_x_y is cur_row_col:
                add_node(x, y, current_x_y)
                stop = current_x_y
            else:
                self.add_long_path(start, stop, locked_x_y, horizontal, tuple_list)  # add_long_path does the sanity check
                '''continue next loop with the current values'''
                start = stop = x if horizontal else y
                locked_x_y = y if horizontal else x

        '''final check after the loop went through'''
        self.add_long_path(start, stop, locked_x_y, horizontal, tuple_list)

        return tuple_list

    @staticmethod
    def squeeze_half_image(image):
        """remove the bottom half of an image"""
        w, h = image.get_size()
        h //= 2
        size = w, h
        return pygame.transform.scale(image, size)

    @staticmethod
    def render_tile(surface, tile):
        """draw single tile"""
        x, y, image = tile

        surface.blit(image, (x, y))

    def clean_sprite(self, sprite):
        """overdraw an old sprite with a clean background"""
        # clear the item
        dirty_rect = self.background.subsurface(sprite.rect)
        self.surface.blit(dirty_rect, sprite.rect)
        # self.lvl_surface.blit(dirty_rect, sprite.rect)

    def add_network_players(self):
        """add players on network level change"""
        for player in Level.players:
            player = self.add_current_player(player.pid)
            Level.players[player.pid] = player

    def add_current_player(self, pid, pos=None):
        """add players to the level only"""
        if pid % 2 is 0:
            pos = self.spawn_player_1_pos if not pos else pos
        else:
            pos = self.spawn_player_2_pos if not pos else pos
        
        sheet = self.PLAYERS[pid % len(self.PLAYERS)]

        new_player = Player(pos, sheet, pid, self.SM_SIZE, self, self.fps)

        return new_player

    def add_player(self, pid, pos=None):
        """add a new player"""
        pid = int(pid)

        new_player = self.add_current_player(pid, pos)
        Level.players.append(new_player)
        log.info("Added Player. Players {}".format(Level.players))

    @staticmethod
    def remove_player(pid):
        """remove a player from the game"""
        try:
            for player in Level.players:
                if player.pid == pid:
                    player.kill()
                    Level.players.remove(player)
            return True
        except (IndexError, AttributeError):
            return False

    def get_all_player_pos(self):
        """resolution independent positions of all players in the map"""
        players_pos = {}
        for player in Level.players:
            normalized_pos = ((player.rect.x - self.margin_left) / player.size,
                              (player.rect.y - self.margin_top) / player.size)
            players_pos[Level.players.index(player)] = normalized_pos
        return players_pos

    def set_player_pos(self, player_id, player_pos):
        """set the player position for all players in the level according to the viewers screen resolution"""
        for player in Level.players:
            if player.pid == int(player_id):
                player.rect.x = round(player_pos[0] * player.size + self.margin_left)
                player.rect.y = round(player_pos[1] * player.size + self.margin_top)
                log.info("Set Player {} position".format(player_id))
                return
        log.info("Cant find player {} to set pos".format(player_id))
        
    
    @staticmethod
    def get_level_info_json():
        # TODO: finish me
        a = []
        for d in Level.players:
            a.append(d.rect.topleft)
        data = {'players': a}
        return data

    @staticmethod
    def set_level_info_via_json(self, json):
        pass
