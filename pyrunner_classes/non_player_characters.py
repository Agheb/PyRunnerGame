from .player import Player
from .state_machine import StateMachine
from .npc_states import *
import pygame

SPRITE_SHEET_PATH = "./resources/sprites/"


class Bots(Player):
    def __init__(self, pos, sheet):
        Player.__init__(self, pos, sheet, bot=True, tile_size=32, fps=25)

        # Create instances of each state
        exploring_state = Exploring(self)
        # list of states in Statemachine
        # {'exploring': <pyrunner_classes.npc_states.Exploring object at 0x0000023A4C5CE9E8>}

        # add states to the state machine
        self.brain = StateMachine()
        self.brain.add_state(exploring_state)
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
            # self.image = self.stop_frame
            elif self.direction == "DL":
                # Dig left/right
                self.image = self.digging_frames_l[self.digging_frame // 4]
                self.digging_frame += 1
                if self.digging_frame is len(self.digging_frames_l) * 4:
                    self.digging_frame = 0
                    self.direction = "Stop"
            elif self.direction == "DR":
                self.image = self.digging_frames_r[self.digging_frame // 4]
                self.digging_frame += 1
                if self.digging_frame is len(self.digging_frames_l) * 4:
                    self.digging_frame = 0
                    self.direction = "Stop"

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
        """kill animation"""
        self.killed = True

