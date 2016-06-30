from .player import Player
from .state_machine import StateMachine
from .npc_states import *
import pygame

SPRITE_SHEET_PATH = "./resources/sprites/"
# TODO: Bots should not collect gold


class Bots(Player):

    def __init__(self, pos, sheet):
        # TODO: Spawn the Bot on other side of map
        # TODO: have spawn points in tilemap set for the bots in each level
        Player.__init__(self, pos, sheet, bot=True, tile_size=32, fps=25)

        self.is_human = False

        # POSITIONAL RELATED
        self.destination = (0, 0)
        self.last_pos = (0, 0)

        # STATEMACHINE RELATED
        # Create instances of each state
        exploring_state = Exploring(self)
        hunting_state = Hunting(self)
        stupid_state = Stupid(self)
        # add states to the state machine
        self.brain = StateMachine()
        self.brain.add_state(exploring_state)
        self.brain.add_state(hunting_state)
        self.brain.add_state(stupid_state)
        # state the npc starts with
        self.brain.set_state('exploring')

        # Load all the left facing images into a list (x, y, height, width)
        self.walking_frames_l = self.sprite_sheet.add_animation(0, 3, 4)
        # Load all the left facing images into a list and flip them to make them face right
        self.walking_frames_r = self.sprite_sheet.flip_list(self.walking_frames_l)
        # Load all the up / down facing images into a list
        self.walking_frames_ud = self.sprite_sheet.add_animation(0, 4, 4)
        # Load the left hanging images into a list
        self.hanging_frames_l = self.sprite_sheet.add_animation(4, 4, 4)
        # Load the left hanging images into a list and flip them to face right
        self.hanging_frames_r = self.sprite_sheet.flip_list(self.hanging_frames_l)
        # death animation
        self.death_frames = self.sprite_sheet.add_animation(5, 5, 8)

        # Stop Frame: Sprite when player is not moving on ground
        self.stop_frame = self.sprite_sheet.add_animation(5, 3)

        self.direction = "Stop"  # direction the player is facing at the beginning of the game

        # Set the image the player starts with
        self.image = self.stop_frame
        # Set a reference to the image rect.
        self.rect = self.image.get_rect()
        # spawn the player at the desired location
        self.rect.topleft = pos

    def process(self):
        self.brain.think()

    def update(self):  # updates the images and creates motion with sprites
        """ Move the player. """
        self.dirty = 1
        self.process()
        Player.update(self)