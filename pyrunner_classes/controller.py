class Controller():
    def __init__(self, player1, config):
        self.player1 = player1
        #self.player2 = player2
        self.config = config


    def interpret_key(self, key):
        """controls and key settings if the game is in foreground"""
        # TODO move both players
        if key == self.config.p1_left:
            self.player1.go_left()
        elif key == self.config.p1_right:
            self.player1.go_right()
        elif key == self.config.p1_up:
            self.player1.go_up()
        elif key == self.config.p1_down:
            self.player1.go_down()
        # TODO actions for both players
        elif key == self.config.p1_action_l:
            print("Player 1 digs left")
        elif key == self.config.p1_action_r:
            print("Player 1 digs right")
        elif key == self.config.p1_interact:
            print("Player 1 interacts")
        elif key == self.config.p1_taunt:
            print("Player 1 taunts")
        # TODO the same for player 2
        elif key == self.config.p2_left:
            print("Player 2 moves left")
        elif key == self.config.p2_right:
            print("Player 2 moves right")
        elif key == self.config.p2_up:
            print("Player 2 moves up")
        elif key == self.config.p2_down:
            print("Player 2 moves down")
        # TODO actions for both players
        elif key == self.config.p2_action_l:
            print("Player 2 digs left")
        elif key == self.config.p2_action_r:
            print("Player 2 digs right")
        elif key == self.config.p2_interact:
            print("Player 2 interacts")
        elif key == self.config.p2_taunt:
            print("Player 2 taunts")
    def release_key(self, key):
        self.player1.schedule_stop()
