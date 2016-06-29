class State(object):
    def __init__(self, name):
        self.name = name

    def do_actions(self):
        pass

    def check_conditions(self):
        pass

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass


class Exploring(State):
    def __init__(self, bot):
        State.__init__(self, "exploring")
        self.bot = bot # set bot this state controlls

    def random_destination(self):
        # TODO Go to Random spot on map
        print("bot goes to random destination")
        return

    def do_actions(self):
        # TODO when walking against something turn around
        print("bot does actions")
        if self.bot.location != self.bot.destination:
            self.bot.go_right()
        return

    def check_conditions(self):
        # TODO Detect player in a specified range and then change state to hunting
        print("bot check conditions")
        return

    def entry_actions(self):
        print("bot check enty actions")
        return

    def exit_actions(self):
        print("bot exit actions")
        return


class Hunting(State):
    # TODO walk towards player position
    # TODO when close to a player, speed up
    def __init__(self, bot):
        State.__init__(self, "hunting")
        self.bot = bot  # set bot this state controlls

    def do_actions(self):
        pass

    def check_conditions(self):
        pass

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass


class Stupid(State):
    def __init__(self, bot):
        State.__init__(self, "stupid")
        self.bot = bot  # set bot this state controlls

    def do_actions(self):
        # TODO determine if player is over or under bot
        # if over go every ladder up / if under down
        # always go on ropes when walking directy onto them
        pass

    def check_conditions(self):
        pass

    def entry_actions(self):
        pass

    def exit_actions(self):
        pass