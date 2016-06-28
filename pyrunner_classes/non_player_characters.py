from .player import Player
from .state_machine import StateMachine
from .npc_states import *

SPRITE_SHEET_PATH = "./resources/sprites/"


class Bots(Player):
    def __init__(self, pos, sheet):
        Player.__init__(self, pos, sheet, bot=True, tile_size=32, fps=25)

        # Create instances of each state
        exploring_state = Exploring(State)

        # add states to the state machine
        self.brain = StateMachine()
        self.brain.add_state(exploring_state)

    def process(self):
        self.brain.think()
        print("bot denkt nach")

