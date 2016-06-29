class StateMachine(object):
    def __init__(self):
        self.stateslist = {}  # store states in a dictionary
        self.active_state = None  # currently active state

    def add_state(self, state):
        # add a state to dictionary of statemachine instance
        self.stateslist[state.name] = state
        print("list of active states in Statemachine")
        print(self.stateslist)
        print("state " + state.name + " added")
        print("number of states in statelist: " + str(len(self.stateslist)))

    def think(self):
        # only continue if there is an active state.
        if not self.active_state:
            print("no state to think, active state is: " + str(self.active_state))
            return
        elif self.active_state:
            print(self.active_state)
            # Perform action of the active state and check conditions
            self.active_state.do_actions()
            print("actions for state " + str(self.active_state) + " performed")

            new_state_name = self.active_state.check_conditions()
            if new_state_name is not None:
                self.set_state(new_state_name)
                print("new state" + new_state_name + "set")

    def set_state(self, new_state_name):
        # change state and perform exit / entry actions
        if self.active_state:
            self.active_state.exit_actions()

        self.active_state = self.stateslist[new_state_name]
        self.active_state.entry_actions

