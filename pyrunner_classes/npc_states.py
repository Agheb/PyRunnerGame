"""
This class and its instances are the states of the bot.
The states determine what the bot does, when to change states, what to do when changing states.
The state_machine controlls the states, it is the brain of the bot.
Bots are Instances of non_player_characters, inherited from player class.
"""
import random
import pygame
from .player import Player
from .level import WorldObject


class State(object):
    def __init__(self, name, bot):
        self.name = name
        self.bot = bot
        self.walking_direction = None
        self.closest_player = None
        self.closest_player_distance = 0
        self.find_ladder = False

    def do_actions(self):
        # Called by the think function in statemachine in each frame.
        # All actions the bot should perform when in this state.
        pass

    def check_conditions(self):
        # Called in every Frame from Statemachine
        # If check_conditions returns a string (name of state), a new active state will be selected
        # and any exit and entry actions will be called from the StateMachine
        pass

    def entry_actions(self):
        # actions the player should do when entering this state
        pass

    def exit_actions(self):
        # actions the player should do when exiting this state
        pass

    def go_to_destination(self):
        # check these conditions after x frames:
        # if destination is right of bot, go_right else go_left
        # if bot collides right or left with not climbable block, change direction
        # if destination under bot and on_ladder, go_down else go_up (catch if up down not possible)
        print("Bot calls go_to_destination with destination set to " + str(self.bot.destination))
        last_x, last_y = self.bot.last_pos
        destination = self.bot.destination
        location = self.bot.get_location()
        print("current bot location: " + str(location))

        dx, dy = destination
        lx, ly = location
        size = (self.bot.rect.right - self.bot.rect.left) // 2

        collision = True if last_x == lx and last_y == ly else False

        if not (lx - size < dx < lx + size and ly - size < dy < ly + size):
            # go right or left towards destination
            if not collision:
                print("no collision")
                if lx < dx:
                    if not self.find_ladder:
                        self.bot.go_right()
                    print("bot goes right")
                elif lx > dx:
                    self.bot.go_left()
                    print("bot goes left")
            else:
                if self.walking_direction == "right":
                    self.bot.go_left()
                    print("bot changes direction to left")
                else:
                    self.bot.go_right()
                    print("bot changes direction to right")

            # go ladders up or down, according to destination
            if dy > ly:
                if self.bot.on_ladder or self.bot.on_rope:
                    self.bot.go_down()
                    print("bot tried to go down")
                elif self.bot.on_rope and dx is lx:
                    self.bot.go_down()
                else:
                    self.find_ladder = True

            elif dy < ly:
                if self.bot.on_ladder:
                    self.bot.go_up()
                    print("bot tried to go up")
                elif self.bot.on_rope and dx is lx:
                    self.bot.go_down()
                else:
                    self.find_ladder = True
        else:
            print("Bot reached destination")
            self.bot.schedule_stop = True
            return True

    def check_closest_player(self):
        # TODO determine which player is closest and return that player position in a radius around bot
        # as destination
        pos_x, pos_y = self.bot.rect.topleft

        for player in Player.group:
            if player.is_human:
                x, y = player.rect.topleft
                distance_x = x - pos_x if x < pos_x else pos_x - x
                distance_y = y - pos_y if y < pos_y else pos_y - y
                distance = distance_x + distance_y

                if not self.closest_player:
                    self.closest_player = player
                    self.closest_player_distance = distance
                elif distance < self.closest_player_distance:
                    self.closest_player = player
                    self.closest_player_distance = distance
        return self.closest_player.get_location() if self.closest_player else False

    def check_destination_reached(self):
        # because of tile based movement, location == destination is not possible.
        # check_destination_reached checks if destination is reached with a margin.
        margin = 16
        destination = self.bot.destination
        location = self.bot.get_location()
        dx, dy = destination
        lx, ly = destination
        x_reached = False
        y_reached = False

        if dx > lx - margin and dx > lx + margin:
            x_reached = True

        elif dy > ly - margin and dy > dy + margin:
            y_reached = True

        if x_reached and y_reached:
            return True

        elif y_reached:
            return "yReached"

        elif x_reached:
            return "xReached"


class Exploring(State):
    def __init__(self, bot):
        State.__init__(self, "exploring", bot)
        self.bot = bot  # set bot this state controlls
        self.first_call = True

    def random_destination(self):
        # TODO Go to Random spot on map
        for tile in WorldObject.group:
            if tile.solid and not tile.climbable_horizontal and random.randint(0, len(WorldObject.group)) % 5 is 0:
                self.bot.destination = tile.rect.midtop

        print("bot destination set: " + str(self.bot.destination))

    def do_actions(self):
        # Set random destination on first call, then change direction every x calls, so every x Frames
        if self.first_call:
            self.random_destination()
            self.first_call = False

        self.go_to_destination()

    def check_conditions(self):
        # TODO Detect player in a specified range and then change state to hunting
        # if player in range, return "hunting"
        # if check_closest_player from super returns a player, let check conditions return "hunting"
        if self.check_closest_player():
            return "hunting"

    def entry_actions(self):
        return

    def exit_actions(self):
        return


class Hunting(State):
    # TODO walk towards player position
    # TODO when close to a player, speed up
    def __init__(self, bot):
        State.__init__(self, "hunting", bot)
        self.bot = bot  # set bot this state controlls

    def do_actions(self):
        self.bot.destination = self.closest_player.get_location() if self.closest_player else self.check_closest_player()
        self.go_to_destination()

    def check_conditions(self):
        # if nearest player is not empty state hunting
        # if another player is now closer, change to state hunting with destination set to the neares player.
        # if nearest player is empty, change state to exploring
        if self.go_to_destination():
            return "exploring"

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass


class Stupid(State):
    def __init__(self, bot):
        State.__init__(self, "stupid", bot)
        self.bot = bot  # set bot this state controlls

    def do_actions(self):
        # if bot is over player go every ladder up / if under down
        self.bot.go_right()

    def check_conditions(self):
        pass

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass
