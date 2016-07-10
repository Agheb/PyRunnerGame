from .state_machine import StateMachine
from .npc_states import *

SPRITE_SHEET_PATH = "./resources/sprites/"


class Bots(Player):

    def __init__(self, bid, pos, sheet, level):
        Player.__init__(self, pos, sheet, None, 32, level, 25, True)

        # POSITIONAL RELATED
        self.bid = bid
        self.destination = (0, 0)
        self.last_pos = (0, 0)
        self.left_tile = None
        self.left_bottom = None
        self.right_tile = None
        self.right_bottom = None
        self.walk_left = True
        self.robbed_gold = None
        # give humans a chance
        self.speed -= self.size / 30
        self.frame_counter = 0
        self.spawning = True
        self.spawn_frame = 0
        # network
        self.network_connector = level.network_connector

        Player.bots.add(self)

        # STATEMACHINE RELATED
        # Create instances of each state
        exploring_state = Exploring(self)
        shortest_state = ShortestPath(self)
        hunting_state = Hunting(self)
        # add states to the state machine
        self.brain = StateMachine()
        self.brain.add_state(exploring_state)
        self.brain.add_state(shortest_state)
        self.brain.add_state(hunting_state)
        # state the npc starts with
        self.brain.set_state('exploring')

        self.spawn_frames = self.sprite_sheet.add_animation(8, 4, 4)
        # Load all the left facing images into a list (x, y, height, width)
        self.walking_frames_l = self.sprite_sheet.add_animation(0, 3, 4)
        # Load all the left facing images into a list and flip them to make them face right
        self.walking_frames_r = self.sprite_sheet.flip_frames(self.walking_frames_l)
        # Load all the up / down facing images into a list
        self.walking_frames_ud = self.sprite_sheet.add_animation(0, 4, 4)
        # Load all falling down frames
        self.falling_frames = self.sprite_sheet.add_animation(5, 3, 4)
        # Load the left hanging images into a list
        self.hanging_frames_l = self.sprite_sheet.add_animation(4, 4, 4)
        # Load the left hanging images into a list and flip them to face right
        self.hanging_frames_r = self.sprite_sheet.flip_frames(self.hanging_frames_l)
        # death animation
        self.death_frames = self.sprite_sheet.reverse_frame_list(self.spawn_frames)

        # Stop Frame: Sprite when player is not moving on ground
        self.stop_frame = self.sprite_sheet.add_animation(5, 3)
        self.stand_left = self.sprite_sheet.add_animation(3, 3)
        self.stand_right = self.sprite_sheet.flip_frames(self.stand_left)
        self.trapped = self.sprite_sheet.add_animation(4, 3)

        self.direction = "Stop"  # direction the player is facing at the beginning of the game

        # Set the image the player starts with
        self.image = self.stop_frame
        # Set a reference to the image rect.
        self.rect = self.image.get_rect()
        # spawn the player at the desired location
        self.rect.topleft = pos

    def go_left(self):
        """add network connector to movement"""
        if self.network_connector.master:
            pass
            # self.network_connector
        super(Player, self).go_left()

    def go_right(self):
        """add network connector to movement"""
        if self.network_connector.master:
            pass
            # self.network_connector
        super(Player, self).go_right()

    def go_up(self):
        """add network connector to movement"""
        if self.network_connector.master:
            pass
            # self.network_connector
        super(Player, self).go_up()

    def go_down(self):
        """add network connector to movement"""
        if self.network_connector.master:
            pass
            # self.network_connector
        super(Player, self).go_down()

    def collect_gold(self, sprite):
        """remove one gold object and drop it on death"""
        self.robbed_gold = sprite
        '''hide the sprite from the screen'''
        self.robbed_gold.rect.topleft = (-1000, -1000)
        self.robbed_gold.dirty = 1

    def restore_gold(self):
        """restore gold above the bot on death"""
        if self.robbed_gold:
            '''restore robbed gold'''
            self.robbed_gold.rect.bottomleft = self.rect.topleft
            self.robbed_gold.got_dropped = True
            self.robbed_gold.dirty = 1

    def death_actions(self):
        """special actions to execute on death which aren't needed for human players"""
        self.restore_gold()
        self.level.bots_respawn.append((self.bid, datetime.now()))

    def process(self):
        """jetzt scharf nachdenken... denk denk denk"""
        if not self.direction == "Trapped":
            if self.frame_counter & 1:
                self.frame_counter = 0
                '''don't think too fast'''
                try:
                    self.brain.think()
                except (TypeError, AttributeError):
                    '''sometimes values are not set fast enough'''
                    pass
            else:
                self.frame_counter += 1

    def update(self):
        """add some bot only behaviour"""
        if self.network_connector.master:
            self.process()
        
        super(Player, self).update()
