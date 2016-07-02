import random
from .player import Player
from .level import WorldObject
from ast import literal_eval as make_tuple
import math


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
        self.walking_direction = None
        self.closest_player = None
        self.closest_player_distance = 0
        self.path = None
        self.next_pos = None
        self.last_direction = 0
        self.go_left = True
        self.switch_direction = False
        self.search_ladder = False
        self.climbed_ladder = False
        self.fps_counter = 0

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

    def walk_the_line(self, x, y, bx, by):
        """Walk according to directions"""
        if self.bot.on_ladder or self.bot.can_go_down:
            if y > by and self.bot.can_go_down:
                self.bot.stop_on_ground = True
                self.bot.go_down()
            elif y < by:
                self.bot.go_up()

            '''save the last walking direction'''
            if self.bot.change_x is not 0:
                self.last_direction = self.bot.speed if x > bx else -self.bot.speed
                self.bot.stop_on_ground = True

        if x < bx:
            self.bot.go_left()
            self.go_left = True
        elif x > bx or bx == 0:
            self.bot.go_right()
            self.go_left = False

    def shortest_path(self):
        """get the shortest path to a target"""
        if self.fps_counter < 12:
            self.fps_counter += 1

            if self.bot.on_tile:
                bx, by = self.bot.on_tile

                if self.next_pos:
                    x, y = self.next_pos

                    # y -= 1  # set it to player height
                    # print(str(self.next_pos))
                    # print(str(self.bot.on_tile))

                    self.walk_the_line(x, y, bx, by)

                    if x == bx or y == by or (self.bot.change_x is 0 and self.bot.change_y is 0):
                        self.next_pos = self.get_next_position()

                '''make the bot walk into the other direction if he is stuck at the level borders'''
                if bx == self.bot.level.cols - 1:
                    self.bot.go_left()
                    self.go_left = True
                elif bx == 0:
                    self.bot.go_right()
                    self.go_left = False
        else:
            self.fps_counter = 0

            player = None
            for p in Player.group:
                if p.is_human:
                    player = p
                    break

            if self.bot.on_tile and player.on_tile:
                target_tile = player.on_tile
                own_tile = self.bot.on_tile
                x, y = target_tile
                bx, by = self.bot.on_tile
                try:
                    self.path = self.bot.level.graph.shortest_path(str(own_tile), str(target_tile))
                    self.next_pos = self.get_next_position()
                except KeyError:
                    # print(own_tile, " or ", target_tile, " were invalid.")
                    if self.bot.on_ladder and by > y:
                        self.bot.go_up()
                    else:
                        self.bot.go_left() if self.go_left else self.bot.go_right()

    def check_closest_player(self):
        # Bot checks if a player is in a specified radius. If its is returns the position of the closest player.
        def distance(p0, p1):
            return math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)

        bot_pos = self.bot.rect.topleft
        radius = 500

        player = None
        for p in Player.group:
            if p.is_human:
                player = p
                break

        if player:
            player_pos = player.rect.topleft
            distance = distance(player_pos, bot_pos)

            if distance < radius:
                if not self.closest_player:
                    self.closest_player = player
                    self.closest_player_distance = distance
                elif distance < self.closest_player_distance:
                    self.closest_player = player
                    self.closest_player_distance = distance
                return player_pos
            else:
                return False


class Exploring(State):
    def __init__(self, bot):
        State.__init__(self, "exploring", bot)
        self.bot = bot  # set bot this state controlls

    def random_destination(self):
        # TODO Go to Random spot on map
        pass

    def do_actions(self):
        self.bot.go_left() if self.go_left else self.bot.go_right()

    def check_conditions(self):
        if self.check_closest_player():
            print("player found")
            return "shortest path"

    def entry_actions(self):
        return

    def exit_actions(self):
        return


class ShortestPath(State):
    def __init__(self, bot):
        State.__init__(self, "shortest path", bot)
        self.bot = bot  # set bot this state controlls
        self.path = None
        self.target = None
        self.next_pos = None
        self.fps_counter = 0
        self.last_direction = self.bot.change_x

    def do_actions(self):
        self.shortest_path()

    def check_conditions(self):
        # if nearest player is not empty state hunting
        # if another player is now closer, change to state hunting with destination set to the neares player.
        # if nearest player is empty, change state to exploring
        if not self.check_closest_player():
            return "exploring"

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass
