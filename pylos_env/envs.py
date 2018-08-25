import gym
import numpy as np
from gym import spaces

from pylos import Pylos


class PylosEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.pylos = Pylos()
        self.done = False
        
        self.reset()
        # discrete 1 = which ball to move (0-29 = from one of the board positions, 30 = from the player's reserve)
        # discrete 2 = where to move the ball
        # discrete 3 = first ball to retract (30 = none)
        # discrete 4 = second ball to retract (30 = none)

        # Initially only 1 out of 31*31*31 moves will be valid; perhaps a better representation is needed?
        self.action_space = spaces.MultiDiscrete([31, 30, 31, 31])

    def state_from_pylos(self):
        state = dict()
        state['current_player'] = self.pylos.current_player
        state['board'] = np.zeros((30, 2))
        board_row = 0
        for layer in self.pylos.layers:
            for row in layer:
                for col in row:
                    if col != None: state['board'][board_row][col] = 1
                    board_row += 1

        return state
        
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

    #TODO: add tests
    def first_available_move(self):
        if self.pylos.reserve[self.pylos.current_player] > 0:
            valid_positions = filter(lambda pos: self.pylos.is_valid_to_position(None, pos), self.pylos.get_all_positions())
            return None, next(valid_positions)

        balls = self.pylos.get_current_player_balls()
        for position in balls:
            # look for first available square which is not above `position`
            for to_position in self.pylos.get_moveup_locations(position):
                return position, to_position

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

