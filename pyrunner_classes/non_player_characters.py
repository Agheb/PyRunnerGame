from .player import Player
from .state_machine import StateMachine
from .npc_states import *
import pygame

SPRITE_SHEET_PATH = "./resources/sprites/"
# TODO: Bots should not collect gold


class Bots(Player):

    def __init__(self, pos, sheet):
        Player.__init__(self, pos, sheet, bot=True, tile_size=32, fps=25)
        # TODO: Spawn the Bot on other side of map
        # TODO: have spawn points in tilemap set for the bots in each level

        # POSITIONAL RELATED
        self.destination = None

        # STATE RELATED
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

    def process(self):
        self.brain.think()
        print("bot denkt nach")

    def update(self):  # updates the images and creates motion with sprites
        """ Move the player. """
        self.dirty = 1
        self.process()

        if not self.killed:
            # Move left/right
            self.rect.x += self.change_x
            self.rect.y += self.change_y
            self.x, self.y = self.rect.topleft

            '''keep the correct movement animation according to the direction on screen'''
            if self.change_x < 0:
                self.direction = "RL" if self.on_rope else "L"
            elif self.change_x > 0:
                self.direction = "RR" if self.on_rope else "R"
            elif not self.on_ground and not self.on_rope:
                self.direction = "UD"

            # Animations with Sprites
            '''movements'''
            if self.direction == "R":
                self.image = self.sprite_sheet.get_frame(self.x, self.walking_frames_r)
            elif self.direction == "L":
                self.image = self.sprite_sheet.get_frame(self.x, self.walking_frames_l)
            elif self.direction == "UD":
                self.image = self.sprite_sheet.get_frame(self.y, self.walking_frames_ud)
            elif self.direction == "RR":
                self.image = self.sprite_sheet.get_frame(self.x, self.hanging_frames_r)
            elif self.direction == "RL":
                self.image = self.sprite_sheet.get_frame(self.x, self.hanging_frames_l)
            elif self.direction == "Stop":
                pass

            # Gravity
            self.calc_gravity()
        else:
            self.image = self.death_frames[self.killed_frame // 2]
            self.killed_frame += 1

            if self.killed_frame is len(self.death_frames) * 2:
                pygame.sprite.DirtySprite.kill(self)

    def calc_gravity(self):
        """ Calculate effect of gravity. """
        # See if we are on the ground and not on a ladder or rope
        if not self.on_ground and not self.on_ladder and not self.on_rope:
            if self.change_y >= 4:
                self.change_y += .35
            else:
                self.change_y = 4

        if self.stop_on_ground:
            if self.change_x is not 0:
                if self.rect.x % self.tile_size is not 0:
                    if self.change_x > 0:
                        self.go_right()
                    else:
                        self.go_left()
                else:
                    self.change_x = 0

            if self.change_y is not 0:
                if self.change_y <= self.speed:
                    # the player is lowered by one for a constant ground collision
                    if (self.rect.y - 1) % self.tile_size is not 0:
                        if self.change_y < 0:
                            self.go_up()
                        else:
                            self.go_down()
                    else:
                        self.change_y = 0

            if self.change_x is 0 and self.change_y is 0:
                self.stop_on_ground = False

    def kill(self):
        # TODO kill player when collision between player and bot
        # TODO kill bot when in hole and respawn at set spawn point in level
        """kill animation"""
        self.killed = True

