#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main pyRunner class which initializes all sub classes and threads"""
# Python 2 related fixes
from __future__ import division
import pytmx
from pytmx.util_pygame import load_pygame
from .level_objecs import *
from .player import Player
from .non_player_characters import Bots
from random import randint
from operator import itemgetter
from .djikstra import Graph
from pprint import pprint as pp
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


# TODO TMX Specification:
# TODO make collidable Rects from ObjectLayers


class Level(object):
    """
    Level object loads tmx-file for game and draws each tile to screen
    filename: Tilesheet and TMX-File must be in same folder
    1. Read in and parse TMX file
    2. load all tilesheet image
    3. draw layer by layer
    """
    PLAYER1 = "LRCharacters32.png"
    PLAYER2 = "LRCharacters32_p2.png"
    SM_SIZE = 32

    levels = []
    players = []

    def __init__(self, surface, path, fps=25):
        self.surface = surface
        self.background = self.surface.copy()
        self.path = path
        self.fps = fps
        self.graph = None
        self.walkable_list = []
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

        '''draw the complete level'''
        self.render()

        '''calculate walking paths'''
        self.generate_paths()

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
            bot_obj = self.tm.get_object_by_name("Enemies")
            bot_pos = self.calc_object_pos((bot_obj.x, bot_obj.y))
        except ValueError:
            '''enemies fall from the sky'''
            bot_pos = randint(0, self.width), 0
        try:
            next_level = self.tm.get_object_by_name("Exit_Gate")
            self.next_level_pos = self.calc_object_pos((next_level.x, next_level.y))
            self.next_level = LEVEL_PATH + next_level.type + LEVEL_EXT
        except ValueError:
            pass

        self.spawn_player_1_pos = p1_pos
        self.spawn_player_2_pos = p2_pos
        self.spawn_enemies_pos = bot_pos

        self.bot_1 = Bots(self.spawn_enemies_pos, "LRCharacters32.png", self)

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

        for layer in self.tm.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                '''first check all layer properties'''
                ladder = check_property(layer, 'climbable')
                rope = check_property(layer, 'climbable_horizontal')
                gold = check_property(layer, 'collectible')
                removable = check_property(layer, 'removable')
                solid = check_property(layer, 'solid')
                width, height = self.tile_width, self.tile_height
                fps = self.fps

                '''create the sprites'''
                for a in layer.tiles():
                    pos_x, pos_y, image = a
                    size = width, height
                    tile_id = pos_x, pos_y

                    pos_x = self.margin_left + (width * pos_x)
                    pos_y = self.margin_top + (height * pos_y)

                    image = pygame.transform.scale(image, size)

                    '''chop off the bottom half in the last row to fit 720p'''
                    if pos_y == self.last_row:
                        image = self.squeeze_half_image(image)

                    a = pos_x, pos_y, image

                    if ladder:
                        Ladder(a, size, tile_id, fps, solid)
                    elif rope:
                        Rope(a, size, tile_id, fps)
                    elif gold:
                        Collectible(a, size, tile_id, fps)
                    elif removable:
                        WorldObject(a, size, tile_id, fps, solid, removable)
                    elif solid:
                        WorldObject(a, size, tile_id, fps, solid)

                    if layer.name == "Background":
                        '''create a blank copy of the background layer'''
                        self.render_tile(self.background, a)
                        self.render_tile(self.surface, a)
                    elif not gold:
                        '''add all tiles that a player can walk on to this list'''
                        x, y = tile_id
                        if y is self.rows - 1:
                            continue
                        if rope:    # treat ropes as a layer below
                            y += 1
                        '''only add walkable tiles'''
                        self.walkable_list.append((x, y))

    def generate_paths(self):
        """create paths by id for bots"""
        start_x = 0
        stop_x = 0
        start_y = 0
        stop_y = 0
        current_col = 0
        current_row = 0
        not_set = True

        # graph to use with dijkstra's shortest path algorithm
        self.graph = Graph()
        # remove duplicate entries (e.g. ropes that count one row deeper)
        self.walkable_list = list(set(self.walkable_list))
        # sort list by x, then by y
        self.walkable_list.sort(key=itemgetter(0))
        self.walkable_list.sort(key=itemgetter(1))

        # print(str(self.walkable_list))

        '''find all horizontal paths'''
        for x, y in self.walkable_list:
            # jump to the next item if there's no first
            if not_set:
                start_x = stop_x = x
                current_row = y
                not_set = False
                continue

            # print(str(x), " ", str(stop_x))
            if x == stop_x + 1 and current_row is y:
                name = "(%s, %s)" % (x, y)
                before = "(%s, %s)" % (x - 1, y)
                self.graph.add_node(name)
                if x is not 0:
                    self.graph.add_edge(name, before, 1)
                    self.graph.add_edge(before, name, 1)
                stop_x = x
            else:
                length = stop_x - start_x
                if length:
                    start = "(%s, %s)" % (start_x, y)
                    end = "(%s, %s)" % (stop_x, y)
                    self.graph.add_edge(start, end, length + 1)
                    self.graph.add_edge(end, start, length + 1)
                # print(str(start_x), " to ", str(stop_x), " row: ", str(row), " length: ", str(length))
                '''
                if length:
                    length += 1  # we start at 0 but want to ignore single tiles (ladders etc.)
                    # self.paths_horizontal.append((start_x, stop_x, current_row, length))
                    # print("adding path from %(start_x)s to %(stop_x)s in row %(current_row)s - length: %(length)s" % locals())
                '''
                # continue next loop with the current values
                start_x = stop_x = x
                current_row = y

        # final check after the loop went through
        if start_x is not stop_x:
            length = stop_x - start_x + 1
            start = "(%s, %s)" % (start_x, current_row)
            stop = "(%s, %s)" % (stop_x, current_row)
            self.graph.add_edge(start, stop, length)
            self.graph.add_edge(stop, start, length)
            '''
            length = stop_x - start_x + 1
            self.paths_horizontal.append((start_x, stop_x, current_row, length))
            '''

        '''find all ladders'''
        ladders = []
        for tile in WorldObject.group:
            if tile.climbable:
                ladders.append(tile.tile_id)
        '''sort them by x value'''
        # remove duplicate entries
        ladders = list(set(ladders))
        # sort list by x, then by y
        ladders.sort()

        not_set = True
        '''convert them to paths'''
        for x, y in ladders:

            if not not_set:
                start_y = stop_y = y
                current_col = x
                not_set = False
                continue

            if y == stop_y + 1 and current_col is x:
                name = "(%s, %s)" % (current_col, y)
                before = "(%s, %s)" % (current_col, y - 1)
                self.graph.add_node(name)
                if y is not 0:
                    self.graph.add_edge(name, before, 1)
                stop_y = y
            else:
                length = stop_y - start_y
                if length:
                    length += 1  # we start at 0 but want to ignore single tiles (ladders etc.)
                    name = "(%s, %s)" % (current_col, start_y)
                    before = "(%s, %s)" % (current_col, stop_y)
                    down = "(%s, %s)" % (current_col, stop_y + 1)
                    self.graph.add_node(down)
                    self.graph.add_edge(before, down, 1)
                    self.graph.add_edge(down, before, 1)
                    self.graph.add_edge(name, down, length + 1)
                    self.graph.add_edge(down, name, length + 1)
                    # self.paths_vertical.append((current_col, start_y, stop_y, length))
                    # print("adding path from %(start_y)s to %(stop_y)s in column %(current_col)s - length: %(length)s" % locals())
                # continue next loop with the current values
                start_y = stop_y = y
                current_col = x

        # final check after the loop went through
        if start_y is not stop_y:
            length = stop_y - start_y + 1
            start = "(%s, %s)" % (current_col, start_y)
            stop = "(%s, %s)" % (current_col, stop_y)
            down = "(%s, %s)" % (current_col, stop_y + 1)
            self.graph.add_node(down)
            self.graph.add_edge(stop, down, 1)
            self.graph.add_edge(start, down, length + 1)
            self.graph.add_edge(down, stop, 1)
            self.graph.add_edge(down, start, length + 1)
            # self.paths_vertical.append((current_col, start_y, stop_y, length))
        #
        # '''cycle through all horizontal sprites and add them all one by one (with path = 1 for neighbours)'''
        # for start, stop, y, length in self.paths_horizontal:
        #     for i in range(start - 1, stop + 2):
        #         name = "(%s, %s)" % (i, y)
        #         before = "(%s, %s)" % (i - 1, y)
        #         if i is not start:
        #             self.graph.add_node(name)
        #             self.graph.add_edge(name, before, 1)
        #         else:
        #             self.graph.add_node(name)
        #
        # '''for the ladders its enough to add start and stop points'''
        # for x, start, stop, length in self.paths_vertical:
        #     s_start = "(%s, %s)" % (x, start)
        #     s_stop = "(%s, %s)" % (x, stop + 1)   # + 1 to connect to the bottom tile
        #     self.graph.add_edge(s_start, s_stop, length)
        #
        #     '''and to add the ladder tiles inbetween'''
        #     for i in range(start, stop + 2):
        #         name = "(%s, %s)" % (x, i)
        #         before = "(%s, %s)" % (x, i - 1)
        #         self.graph.add_node(name)
        #         self.graph.add_edge(before, name, 1)

        # print(self.graph)
        # print(self.graph.shortest_path('20, 4', '5, 7'))
        # print(str(self.paths_horizontal))
        # print(str(self.paths_vertical))

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

    def add_player(self, pid, pos=None, fps=25):
        """add a new player"""
        pid = int(pid)

        if pid % 2 is 0:
            pos = self.spawn_player_1_pos if not pos else pos
            sheet = self.PLAYER1
        else:
            pos = self.spawn_player_2_pos if not pos else pos
            sheet = self.PLAYER2

        new_player = Player(pos, sheet, pid, self.SM_SIZE, self, self.fps)
        Level.players.append(new_player)
        log.info("Added Player. Players {}".format(Level.players))

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