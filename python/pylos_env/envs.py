import gym
import numpy as np
from gym import spaces

import pylos
from pylos import Pylos


class PylosEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.pylos = Pylos()
        self.done = False

        self.reset()

        # each move consists of 31 possible values (0-29 meaning one of the board positions,
        # 30 meaning 'none' or 'reserve' depending on the current phase)
        self.action_space = spaces.Discrete(31)

    def state_from_pylos(self):
        # current player (0/1) -> consider 2 nodes?
        net_inputs = [self.pylos.current_player]

        # game phase
        net_inputs += [
            1 if self.pylos.phase == pylos.PHASE_SOURCE_LOCATION else 0,
            1 if self.pylos.phase == pylos.PHASE_TARGET_LOCATION else 0,
            1 if self.pylos.phase == pylos.PHASE_RETRACT1 else 0,
            1 if self.pylos.phase == pylos.PHASE_RETRACT2 else 0
        ]

        # board (3 nodes per board position
        net_inputs += [ 1 if ball_owner is None else 0 for ball_owner in self.flat_board() ]
        net_inputs += [ 1 if ball_owner == 0 else 0 for ball_owner in self.flat_board() ]
        net_inputs += [ 1 if ball_owner == 1 else 0 for ball_owner in self.flat_board() ]

        return np.array(net_inputs)

    def flat_board(self):
        result = []
        for l in self.pylos.layers:
            for r in l:
                result += r
        return result
        
    def reset(self):
        self.done = False
        self.pylos = Pylos()
        return self.state_from_pylos()

    def map_action_to_game_move(self, action):
        from_position = self.map_action_space_to_game_coordinates(action[0])
        to_position = self.map_action_space_to_game_coordinates(action[1])

        retract1 = self.map_action_space_to_game_coordinates(action[2])
        retract2 = self.map_action_space_to_game_coordinates(action[3])
        retractions = []

        if retract1 is not None: retractions.append(retract1)
        if retract2 is not None: retractions.append(retract2)

        return from_position, to_position, retractions

    def step(self, action):
        if self.done:
            print("WARNING: step called after done")
            return self.state_from_pylos(), 0, self.done, {'warning_step_after_done': True}

        from_position, to_position, retractions = self.map_action_to_game_move(action)

        # attemt move as-is
        if from_position is None:
            valid = self.pylos.move_from_reserve(to_position, retractions)
        else:
            valid = self.pylos.move_up(from_position, to_position, retractions)
        info = {}

        # find a valid move when none was available
        if not valid:
            alt_move = self.first_available_move()
            from_pos, to_pos = alt_move
            if from_pos is None:
                self.pylos.move_from_reserve(to_pos)
            else:
                self.pylos.move_up(from_pos, to_pos)

            info = {'invalid_move': not valid, 'alt_move': alt_move}

        winner = self.pylos.get_winner()
        reward = 0
        if winner is not None:
            reward = 1
            self.done = True

        return self.state_from_pylos(), reward, self.done, info

    def map_action_space_to_game_coordinates(self, action_value):
        if action_value < 16:
            return 0, int(action_value / 4), action_value % 4
        action_value -= 16
        if action_value < 9:
            return 1, int(action_value / 3), action_value % 3
        action_value -= 9
        if action_value < 4:
            return 2, int(action_value / 2), action_value % 2
        action_value -= 4
        if action_value == 0:
            return 3, 0, 0
        return None

