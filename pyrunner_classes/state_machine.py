#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

log = logging.getLogger("State Machine")


class StateMachine(object):
    """switch between different states"""
    def __init__(self):
        self.states_list = {}  # store states in a dictionary
        self.active_state = None  # currently active state

    def add_state(self, state):
        """add a state to dictionary of statemachine instance"""
        self.states_list[state.name] = state
        log.debug("list of active states in Statemachine")
        log.debug(self.states_list)
        log.debug("state " + state.name + " added")
        log.debug("number of states in statelist: " + str(len(self.states_list)))

    def think(self):
        """only continue if there is an active state."""
        if not self.active_state:
            log.info("no state to think, active state is: " + str(self.active_state))
            return
        else:
            log.debug(self.active_state)
            '''Perform action of the active state and check conditions'''
            self.active_state.do_actions()
            log.debug("actions for state " + str(self.active_state) + " performed")

            new_state_name = self.active_state.check_conditions()
            if new_state_name:
                self.set_state(new_state_name)
                log.debug("new state " + new_state_name + " set")

    def set_state(self, new_state_name):
        """change state and perform exit / entry actions"""
        if self.active_state:
            self.active_state.exit_actions()

        self.active_state = self.states_list[new_state_name]
        self.active_state.entry_actions()
        log.info("state " + str(self.active_state) + " set")
