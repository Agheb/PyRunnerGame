class StateMachine(object):
    def __init__(self):
        self.stateslist = {}  # store states in a dictionary
        self.active_state = None  # currently active state

    def add_state(self, state):
        # add a state to dictionary of statemachine instance
        self.stateslist[state.name] = state
        print("list of states in Statemachine" + str(self.stateslist))

    def think(self):
        # only continue if there is an active state
        if not self.active_state:
            print("no state to think, active state is: " + str(self.active_state))
            return

        # Perform action of the active state
        self.active_state.do_actions()
        print("actions for state " + self.active_state + "performed")

        new_state_name = self.active_state.check_conditions()
        if new_state_name is not None:
            self.set_state(new_state_name)
            print("new state" + new_state_name + "set")

    def set_state(self, new_state_name):
        # change state and perform exit / entry actions
        if self.active_state:
            self.active_state.exit_actions()

        self.active_state = self.stateslist[new_state_name]
        self.active_state.entry_action

