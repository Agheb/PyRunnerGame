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
        self.bot = bot

    def random_destination(self):
        print("bot goes to random destination")

    def do_actions(self):
        print("bot does actions")

    def check_conditions(self):
        print("bot check conditions")

    def entry_actions(self):
        print("bot check enty actions")

    def exit_actions(self):
        print("bot exit actions")
