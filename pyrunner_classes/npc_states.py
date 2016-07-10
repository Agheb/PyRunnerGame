from .player import Player
from ast import literal_eval as make_tuple
from datetime import datetime
from .actions import Action
import logging
import math
import pygame

log = logging.getLogger("Npc States")


class State(object):
    """
        This class and its instances are the states of the bot.
        The states determine what the bot does, when to change states, what to do when changing states.
        The state_machine controlls the states, it is the brain of the bot.
        Bots are Instances of non_player_characters, inherited from player class.
    """

    def __init__(self, name, bot):
        self.name = name
        self.bot = bot
        self.bot_last_tile = None
        self.closest_player = None
        self.cp_distance = 0
        self.cp_last_tile = None
        self.path = None
        self.next_pos = None
        self.old_pos = None
        self.last_direction = 0
        self.switch_direction = False
        self.search_ladder = False
        self.climbed_ladder = False
        self.detection_range = 10

    def do_actions(self):
        """
            Called by the think function in statemachine in each frame.
            All actions the bot should perform when in this state.
        """
        pass

    def check_conditions(self):
        """
            Called in every Frame from Statemachine
            If check_conditions returns a string (name of state), a new active state will be selected
            and any exit and entry actions will be called from the StateMachine
        """
        pass

    def entry_actions(self):
        """actions the player should do when entering this state"""
        pass

    def exit_actions(self):
        """actions the player should do when exiting this state"""
        pass

    def get_next_position(self):
        """return the next tile to walk to"""
        if self.path:
            length, pos_list = self.path
        else:
            pos_list = False

        return make_tuple(pos_list.pop(0)) if pos_list else False

    def get_path_length(self, own_path=None):
        """return the length of the path"""
        check_path = own_path if own_path else self.path
        length, pos_list = check_path
        return length if self.path else 0

    def walk_the_line(self, x, y, bx, by):
        """Walk according to directions"""
        if self.bot.direction == "Trapped":
            return

        log.debug("walking from %(bx)s/%(by)s to %(x)s/%(y)s" % locals())

        if y != by and (self.bot.on_ladder or self.bot.can_go_down):
            if self.bot.left_tile and self.bot.left_tile.is_rope and x < bx:
                '''climb on ropes which are connected to ladders etc. left of the player'''
                # self.bot.stop_on_ground = True
                self.bot.change_y = 0
                # get past ground collisions
                self.bot.on_rope = True
                self.bot.rect.y = self.bot.left_tile.rect.y
                self.bot.rect.x -= self.bot.speed
                # go left
                self.bot.go_left()
                self.bot.walk_left = True
            elif self.bot.right_tile and self.bot.right_tile.is_rope and bx < x:
                '''climb on ropes which are connected to ladders etc. right of the player'''
                # self.bot.stop_on_ground = True
                self.bot.change_y = 0
                # get past ground collisions
                self.bot.on_rope = True
                self.bot.rect.y = self.bot.right_tile.rect.y
                self.bot.rect.x += self.bot.speed
                # go right
                self.bot.go_right()
                self.bot.walk_left = False
            elif y > by and (self.bot.can_go_down or self.bot.on_ladder):
                '''use ladders solid top spots to climb down'''
                self.bot.change_x = 0
                self.bot.go_down()
            elif y < by and self.bot.on_ladder:
                '''or simply climb up'''
                self.bot.change_x = 0
                self.bot.go_up()
        elif y > by and self.bot.on_rope and (x - 2 <= bx <= x + 2 or not self.bot.change_x):
            '''jump down of ropes if the player is walking below the bot'''
            jump_down = True  # make sure the bot jumps off a rope if he's stuck

            if self.bot.change_x:
                '''check if there's nothing in the way to the player'''
                for tile in self.bot.level.walkable_list:
                    tx, ty = tile
                    if bx is tx:
                        if by < ty < y:
                            jump_down = False
                        elif ty >= y:
                            break
            '''then jump down'''
            if jump_down:
                self.bot.change_x = 0
                self.bot.go_down()
        elif x < bx:
            '''else simply go to the left if the player is on the left or we hit the right border'''
            self.bot.go_left()
            self.bot.walk_left = True
        elif bx < x:
            '''or right if the player is on the right or we hit the left border'''
            self.bot.go_right()
            self.bot.walk_left = False

        self.check_world_borders()

    def calc_shortest_paths(self, own_tile, target_tile):
        """check all players for who's closest"""
        try:
            return self.bot.level.graph.shortest_path(own_tile, target_tile)
        except KeyError:
            log.info("Error: ", str(own_tile), " ", str(target_tile))
            return False

    def shortest_path(self):
        """get the shortest path to a target"""
        if self.bot.on_tile:
            '''calculate which player is the closest'''
            own_tile = self.bot.on_tile

            player = None
            path = None
            length = 0
            for p in Player.group:
                if p.is_human and p.on_tile:
                    target_tile = p.on_tile

                    new_path = self.calc_shortest_paths(own_tile, target_tile)
                    if new_path:
                        new_len = self.get_path_length(new_path)
                        length = new_len if not length else length

                        if new_len < length:
                            player = p
                            path = new_path
                            length = new_len

            return path if player else False

    def check_player_in_range(self):
        """find the closest player in a circle ratio"""
        collide_rect = pygame.sprite.collide_rect_ratio(self.detection_range)

        players_in_range = pygame.sprite.spritecollide(self.bot, Player.humans, False, collided=collide_rect)

        if len(players_in_range) > 1:
            self.check_closest_player(players_in_range)
        elif len(players_in_range) == 1:
            return players_in_range[0]
        else:
            return None

    def check_closest_player(self, players=None):
        """Bot checks if a player is in a specified radius. If its is returns the position of the closest player."""

        def distance(p0, p1):
            """calculate the distance to a player"""
            return math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2) if p0 and p1 else radius

        bot_pos = self.bot.on_tile
        radius = self.detection_range  # tiles!! (not pixels)

        player = None
        new_distance = radius
        last_tile = None

        if not players:
            players = Player.humans

        for p in players:
            if p.on_tile:
                distance = distance(p.on_tile, bot_pos)
                last_tile = p.on_tile

                '''save the first player as target if there's none, else the closest one'''
                if distance < new_distance:
                    player = p
                    new_distance = distance

        if player:
            self.closest_player = player
            self.cp_distance = new_distance
            self.cp_last_tile = last_tile

            return player
        else:
            return None

    def check_world_borders(self):
        """change walking direction if the bot hits the border"""
        if self.bot.on_tile:
            bx, by = self.bot.on_tile

            '''
                check for collisions with other sprites:
                note that all sprites that shouldn't collide with the bot are excluded in game_physics.py
            '''
            if self.bot.left_tile and not self.bot.left_tile.is_rope:
                # log.info("collision: ", str(self.bot.left_tile), " ", str(self.bot.left_tile.is_rope))
                self.bot.walk_left = False
            elif self.bot.right_tile and not self.bot.right_tile.is_rope:
                # log.info("collision: ", str(self.bot.right_tile), " ", str(self.bot.left_tile.is_rope))
                self.bot.walk_left = True

            if bx == self.bot.level.cols - 1:
                self.bot.walk_left = True
            elif bx == 0 and not self.bot.on_ladder:
                self.bot.walk_left = False

            self.bot.go_left() if self.bot.walk_left else self.bot.go_right()


class Exploring(State):
    """wander around the map"""

    def __init__(self, bot):
        State.__init__(self, "exploring", bot)

    def do_actions(self):
        """if the player can move we will walk around the map until we find a close player"""
        if self.bot.direction is not "Trapped":
            '''if there's no shortest path walk around and lookout for players'''
            if self.bot.on_tile:
                x, y = bx, by = self.bot.on_tile

                if self.next_pos is not self.old_pos:
                    if self.bot.on_ladder or self.bot.can_go_down:
                        if self.bot.on_ladder or self.bot.change_y < 0:
                            y = by - 1
                            self.climbed_ladder = True
                        elif self.bot.can_go_down and not self.climbed_ladder and not self.bot.can_jump_off:
                            self.bot.stop_on_ground = True
                            y = by + 1

                        if not self.bot.change_y and self.climbed_ladder:
                            self.climbed_ladder = False
                            '''make sure the bot doesn't fall off ladders when they have an empty gap next to them'''
                            if not self.bot.left_bottom:
                                self.bot.walk_left = False
                            elif not self.bot.right_bottom:
                                self.bot.walk_left = True
                    else:
                        x = bx - 1 if self.bot.walk_left else bx + 1

                    self.walk_next_tile(x, y, bx, by)
                else:
                    # x = bx - 1 if self.bot.walk_left else bx + 1
                    self.walk_next_tile(x, y, bx, by)

    def walk_next_tile(self, x, y, bx, by):
        """store the current positions and proceed"""
        self.old_pos = bx, by
        self.next_pos = x, y

        self.walk_the_line(x, y, bx, by)

    def check_conditions(self):
        """as soon as a player is in sight switch to a hunting mode"""
        if self.check_player_in_range():
            log.info("player found")
            return "shortest path"

    def entry_actions(self):
        """check these conditions when entering this state"""
        return

    def exit_actions(self):
        """perform these actions when switching state"""
        return


class ShortestPath(State):
    """Hunt a player using Dijkstra's shortest path algorithm"""

    def __init__(self, bot):
        State.__init__(self, "shortest path", bot)

    def do_actions(self):
        """walk along the path"""
        if not self.next_pos:
            '''1. get the next position'''
            if self.path:
                self.next_pos = self.get_next_position()

                if not self.next_pos:
                    '''if the position is invalid go on to step 2'''
                    self.path = self.next_pos = None

        if not self.path and self.closest_player and self.closest_player.on_tile and self.bot.on_tile:
            '''2. recreate a path if step 1 failed'''
            self.path = self.calc_shortest_paths(self.bot.on_tile, self.closest_player.on_tile)
            self.next_pos = self.get_next_position()

        if self.next_pos:
            bx, by = self.bot_last_tile = self.bot.on_tile if self.bot.on_tile else self.bot_last_tile

            if self.closest_player:
                self.cp_last_tile = self.closest_player.on_tile

            x, y = self.next_pos

            self.walk_the_line(x, y, bx, by)

            if x == bx or y == by or (not self.bot.change_x and not self.bot.change_y):
                self.old_pos = self.next_pos
                '''get the next valid position / empty the path to create a new one'''
                self.next_pos = self.get_next_position()

                # log.info("trying to get a new position: ", str(self.next_pos), " old: ", str(self.old_pos))
                if self.next_pos is self.old_pos:
                    self.next_pos = self.old_pos = None

    def check_conditions(self):
        """
            if there's no path switch to exploring mode
        """
        if not self.path and not self.next_pos:
            return "hunting"

    def entry_actions(self):
        """look up a shortest path if entering this state"""
        self.closest_player = self.check_player_in_range()

        if not self.path:
            if self.bot.on_tile and self.closest_player.on_tile:
                self.path = self.calc_shortest_paths(self.bot.on_tile, self.closest_player.on_tile)
                self.next_pos = self.get_next_position()

    def exit_actions(self):
        """perform these when leaving this state"""
        self.next_pos = None


class Hunting(Exploring):
    """Hunt a player using a simple/stupid move to player x/y algorithm"""

    def __init__(self, bot):
        State.__init__(self, "hunting", bot)
        self.check_sp = False
        self.change_layer = False
        self.switch_time = None

    def do_actions(self):
        """walk along the path"""

        if self.bot.direction is not "Trapped":
            '''if there's no shortest path search for the closest player'''
            if self.bot.on_tile and self.closest_player and self.closest_player.on_tile:
                x, y = self.closest_player.on_tile
                bx, by = self.bot.on_tile

                if self.bot.on_tile is not self.old_pos:
                    self.check_sp = True

                if by == y:
                    self.change_layer = False
                    self.bot.walk_left = True if x < bx else False
                else:
                    self.change_layer = True

                if self.change_layer:
                    if self.bot.on_rope or self.bot.on_ladder or self.bot.can_go_down:
                        self.walk_the_line(x, y, bx, by)
                else:
                    '''make the bot walk into the other direction if he is stuck at the level borders'''
                    self.check_world_borders()

                self.old_pos = self.bot.on_tile

    def check_conditions(self):
        """if there's no path switch to exploring mode"""
        '''make sure the player still exists'''
        if not self.closest_player:
            '''else wander along until you find a new one'''
            return "exploring"
        if self.check_sp and (datetime.now() - self.switch_time).seconds >= 1:
            '''check if there's a shortest path to the target'''
            return "shortest path"

    def entry_actions(self):
        """look up the closest player when entering this state"""
        self.closest_player = self.check_player_in_range()
        self.switch_time = datetime.now()

    def exit_actions(self):
        """perform these when leaving this state"""
        self.check_sp = False
