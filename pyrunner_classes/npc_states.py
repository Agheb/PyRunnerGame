import random
from .player import Player
from .level import WorldObject


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

    def go_to_destination(self):
        """
            check these conditions after x frames:
            if destination is right of bot, go_right else go_left
            if bot collides right or left with not climbable block, change direction
            if destination under bot and on_ladder, go_down else go_up (catch if up down not possible)
        """
        # print("Bot calls go_to_destination with destination set to " + str(self.bot.destination))
        last_x, last_y = self.bot.last_pos
        destination = self.bot.destination
        location = self.bot.get_location()
        self.bot.last_pos = location

        if self.fps_counter is 25:
            mod = True
            self.fps_counter = 0
        else:
            mod = False
            self.fps_counter += 1

        dx, dy = destination
        lx, ly = location
        size = self.bot.size // 2

        # collision = True if self.bot.change_x is 0 and self.bot.change_y is 0 else False
        if self.bot.change_x is 0 and self.bot.change_y is 0:
            collision = True if not self.last_direction else False
            self.last_direction = 0
        else:
            collision = False

        if destination is not location and self.bot.direction is not "Trapped":
            '''only run every second so the bot won't change it's mind too fast'''
            if mod:
                if self.bot.on_ladder and dy < ly:
                    '''go ladders up'''
                    self.bot.go_up()
                    self.climbed_ladder = True
                elif self.bot.can_go_down and dy > ly:
                    '''and down'''
                    self.bot.go_down()
                    self.climbed_ladder = True
                elif self.climbed_ladder:
                    '''after switching platform go into the direction of the player'''
                    self.go_left = True if dx < lx else False
                else:
                    '''if the ladder doesn't go into the desired direction move on'''
                    self.bot.change_x = self.last_direction

                if dx is not lx and (not self.bot.on_ladder or self.bot.change_y is 0):
                    '''search the next ladder if the target is on a different height'''
                    if dy is not ly:
                        self.search_ladder = True

                    if self.go_left:
                        self.bot.go_left()
                        '''go left until you collide or find a ladder'''
                        if collision and not self.climbed_ladder:
                            self.go_left = False
                        self.climbed_ladder = False
                    else:
                        self.bot.go_right()
                        '''if the bot collided go right until you find a ladder'''
                        if collision and not self.climbed_ladder:
                            self.go_left = True
                        self.climbed_ladder = False
            else:
                '''if we find a ladder stop on the current tile and save the last walking direction'''
                if self.search_ladder:
                    if self.bot.on_ladder or self.bot.can_go_down:
                        self.search_ladder = False
                        if self.bot.change_x is not 0:
                            self.last_direction = self.bot.change_x
                            self.bot.stop_on_ground = True
                else:
                    '''jump off a rope if we are above a player'''
                    if self.bot.on_rope and lx - size < dx < lx + size:
                        self.bot.go_down()
        else:
            print("Bot reached destination")
            self.bot.stop_on_ground = True
            return True

    def check_closest_player(self):
        """get the closest player to the bot"""
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
        """check if the bot reached the destination which was set"""
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
            if tile.solid and not tile.climbable_horizontal and random.randint(0, len(WorldObject.group)) % 5:
                x, y = tile.tile_id
                if y != 22:     # ignore items in the last row (23 - 1)
                    '''aim for the player position above the block'''
                    self.bot.destination = tile.rect.centerx, tile.rect.top - (self.bot.size // 2)
                    break

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
