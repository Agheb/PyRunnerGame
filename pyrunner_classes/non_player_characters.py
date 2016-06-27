from .player import Player

class Ninja(Player):
    def __init__(self, pos, sheet):
        Player.__init__(self, pos, sheet, bot=True, tile_size=32, fps=25)

