"""
This class and its instances are the states of the bot.
The states determine what the bot does, when to change states, what to do when changing states.
The state_machine controlls the states, it is the brain of the bot.
Bots are Instances of non_player_characters, inherited from player class.
"""
import random
import pygame


class State(object):
    def __init__(self, name):
        self.name = name

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
        pass


class Stupid(State):
    def __init__(self, bot):
        State.__init__(self, "stupid")
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


class Exploring(State):
    def __init__(self, bot):
        State.__init__(self, "exploring")
        self.bot = bot  # set bot this state controlls

    def random_destination(self):
        # TODO Go to Random spot on map
        print("bot calls random destination")
        info_object = pygame.display.Info()
        screen_width = info_object.current_w
        screen_height = info_object.current_h
        self.bot.destination = (random.randint(0, screen_width), random.randint(0, screen_height))
        print("bot destination set: " + str(self.bot.destination))
        return self.bot.destination

    def do_actions(self):
        # TODO go towards random destination
        print("bot starts actions")
        # change direction every 30 calls, so every 30 Frames
        if random.randint(0, 30) == 1:
            self.random_destination()
        self.go_to_destination()

    def check_conditions(self):
        # TODO Detect player in a specified range and then change state to hunting
        # if player in range, return "hunting"
        # check_closest_player
        print("bot check conditions")
        return

    def entry_actions(self):
        print("bot check entry actions")
        return

    def exit_actions(self):
        print("bot exit actions")
        return

    def go_to_destination(self):
        # check these conditions after x frames:
        # if destination is right of bot, go_right else go_left
        # if bot collides right or left with not climbable block, change direction
        # if destination unter bot and on_ladder, go_down else go_up
        pass

    def check_closest_player(self):
        # TODO determine if player is over or under bot and which player is closest
        pass


class Hunting(State):
    # TODO walk towards player position
    # TODO when close to a player, speed up
    def __init__(self, bot):
        State.__init__(self, "hunting")
        self.bot = bot  # set bot this state controlls

    def do_actions(self):
        # set desttination to nearest player location
        pass

    def check_conditions(self):
        # if nearest player is not empty state hunting
        # if another player is now closer, change to state hunting with destination set to the neares player.
        # if nearest player is empty, change state to exploring
        pass

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass

    def go_to_destination(self):
        # check these conditions after x frames:
        # if destination is right of bot, go_right else go_left
        # if bot collides right or left with not climbable block, change direction
        # if destination unter bot and on_ladder, go_down else go_up
        pass