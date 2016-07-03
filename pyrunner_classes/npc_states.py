import random
from .player import Player
from .level_objecs import WorldObject
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

        if self.bot.on_ladder or self.bot.can_go_down:
            if self.bot.left_tile and self.bot.left_tile.climbable_horizontal and x < bx:
                '''climb on ropes which are connected to ladders etc. left of the player'''
                self.bot.change_y = 0
                # get past ground collisions
                self.bot.on_rope = True
                self.bot.rect.y = self.bot.left_tile.rect.y
                self.bot.rect.x -= self.bot.speed
                # go left
                self.bot.go_left()
                self.bot.walk_left = True
            elif self.bot.right_tile and self.bot.right_tile.climbable_horizontal and bx < x:
                '''climb on ropes which are connected to ladders etc. right of the player'''
                self.bot.change_y = 0
                # get past ground collisions
                self.bot.on_rope = True
                self.bot.rect.y = self.bot.right_tile.rect.y
                self.bot.rect.x += self.bot.speed
                # go right
                self.bot.go_right()
                self.bot.walk_left = False
            elif y > by and (self.bot.can_go_down or (self.bot.on_ladder and self.bot.jump_off_rope)):
                '''use ladders solid top spots to climb down'''
                self.bot.stop_on_ground = True
                self.bot.go_down()
            elif y < by and self.bot.on_ladder:
                '''or simply climb up'''
                self.bot.change_x = 0
                self.bot.go_up()
        elif y > by and self.bot.on_rope and (x - 2 <= bx <= x + 2 or not self.bot.change_x):
            '''jump down of ropes if the player is walking below the bot'''
            jump_down = True    # make sure the bot jumps off a rope if he's stuck

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
        if x < bx:
            '''else simply go to the left if the player is on the left or we hit the right border'''
            self.bot.go_left()
            self.bot.walk_left = True
        elif bx < x:
            '''or right if the player is on the right or we hit the left border'''
            self.bot.go_right()
            self.bot.walk_left = False

        self.check_world_borders()

    def find_your_way(self):
        """walk along to a path"""
        if self.next_pos and self.bot.on_tile:
            x, y = self.next_pos
            bx, by = self.bot.on_tile

            self.walk_the_line(x, y, bx, by)

            '''get a new position if we reached our target'''
            if x == bx or y == by:  # or (self.bot.change_x is 0 and self.bot.change_y is 0):
                new_x = bx
                new_y = by
                if self.bot.on_rope:
                    new_x += 1 if self.bot.change_x > 0 else -1
                elif self.bot.left_tile and self.bot.left_tile.climbable_horizontal:
                    new_x -= 1
                elif self.bot.right_tile and self.bot.right_tile.climbable_horizontal:
                    new_x += 1
                elif y < by and self.bot.on_ladder:
                    print("fyw up")
                    new_y = by - 1
                    self.climbed_ladder = True
                elif y > by and self.bot.can_go_down and not self.climbed_ladder:
                    print("fyw down")
                    new_y = by + 1
                '''store the changed position'''
                if new_x is not bx and new_y is not by:
                    self.next_pos = new_x, new_y

                if not self.bot.change_y and not self.bot.change_x and self.climbed_ladder:
                    self.climbed_ladder = False

            elif self.bot.change_y <= 0 and self.bot.on_ladder and not self.climbed_ladder:
                new_y = by - 1
                self.next_pos = bx, new_y
                self.climbed_ladder = True

    def calc_shortest_paths(self, own_tile, target_tile):
        """check all players for who's closest"""
        try:
            return self.bot.level.graph.shortest_path(own_tile, target_tile)
        except KeyError:
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

    def check_closest_player(self):
        """Bot checks if a player is in a specified radius. If its is returns the position of the closest player."""
        def distance(p0, p1):
            """calculate the distance to a player"""
            return math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2) if p0 and p1 else radius

        bot_pos = self.bot.on_tile
        radius = 10     # tiles!! (not pixels)

        player = None
        new_distance = radius
        last_tile = None

        for p in Player.group:
            if p.is_human and p.on_tile:
                distance = distance(p.on_tile, bot_pos)
                last_tile = p.on_tile

                '''save the first player as target if there's none, else the closest one'''
                if distance < new_distance:
                    player = p
                    new_distance = distance
                    print(str(distance))

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

            if bx == self.bot.level.cols - 1:
                self.bot.go_left()
                self.bot.walk_left = True
            elif bx == 0:
                self.bot.go_right()
                self.bot.walk_left = False


class Exploring(State):
    """wander around the map"""
    def __init__(self, bot):
        State.__init__(self, "exploring", bot)

    def random_destination(self):
        """walk to random destination"""
        own_tile = self.bot.on_tile

        if own_tile:
            bx, by = own_tile

            for obj in WorldObject.group:
                obj_tile = obj.tile_id
                x, y = obj_tile
                check_x = bx - x if bx > x else x - bx
                check_y = by - y if by > y else y - by

                '''check for a tile next to you'''
                if check_x <= 10 and check_y <= 3 and own_tile is not obj_tile:
                    if random.randint(0, 10) is 7:
                        if y > by and self.bot.change_y >= 0:
                            return obj_tile
                        elif y < by and self.bot.change_y < 0:
                            return obj_tile
                        elif x < bx and self.bot.walk_left:
                            return obj_tile
                        elif x > bx and not self.bot.walk_left:
                            return obj_tile

        return False

    def do_actions(self):
        """if the player can move we will walk around the map until we find a close player"""
        if self.bot.direction is not "Trapped":
            '''if there's no shortest path search for the closest player'''
            if self.bot.on_tile:
                if self.next_pos is not self.old_pos:
                    self.old_pos = self.next_pos
                    self.find_your_way()
                else:
                    self.next_pos = self.random_destination()

    def check_conditions(self):
        """as soon as a player is in sight switch to a hunting mode"""
        if self.check_closest_player():
            print("player found")
            return "shortest path"

    def entry_actions(self):
        return

    def exit_actions(self):
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

            # print("walking from %(bx)s/%(by)s to %(x)s/%(y)s" % locals())
            self.walk_the_line(x, y, bx, by)  # find_your_way()

            if x == bx or y == by or (not self.bot.change_x and not self.bot.change_y):
                self.old_pos = self.next_pos
                '''get the next valid position / empty the path to create a new one'''
                self.next_pos = self.get_next_position()

                # print("trying to get a new position: ", str(self.next_pos), " old: ", str(self.old_pos))
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
        self.closest_player = self.check_closest_player()

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

    def do_actions(self):
        """walk along the path"""

        if self.bot.direction is not "Trapped":
            '''if there's no shortest path search for the closest player'''
            if self.bot.on_tile and self.closest_player and self.closest_player.on_tile:
                x, y = self.closest_player.on_tile
                bx, by = self.bot.on_tile

                if self.bot.on_tile is not self.old_pos:
                    self.old_pos = self.bot.on_tile
                    self.check_sp = True

                if by is y:
                    self.change_layer = False
                    self.bot.walk_left = True if x < bx else False
                else:
                    self.change_layer = True

                if self.change_layer and (self.bot.on_rope or self.bot.on_ladder or self.bot.can_go_down):
                    self.walk_the_line(x, y, bx, by)
                else:
                    '''make the bot walk into the other direction if he is stuck at the level borders'''
                    self.bot.walk_left = True if x < bx else False
                    self.bot.go_left() if self.bot.walk_left else self.bot.go_right()
                    self.check_world_borders()

    def check_conditions(self):
        """if there's no path switch to exploring mode"""
        '''make sure the player still exists'''
        if not self.closest_player:
            '''else wander along until you find a new one'''
            return "exploring"
        if self.check_sp:
            '''check if there's a shortest path to the target'''
            self.check_sp = False
            return "shortest path"

    def entry_actions(self):
        """look up the closest player when entering this state"""
        self.closest_player = self.check_closest_player()

    def exit_actions(self):
        """perform these when leaving this state"""
        pass

