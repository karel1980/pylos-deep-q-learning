import gym
import numpy as np
from gym import spaces

import pylos
from pylos import Pylos


PHASE_NAMES = [
    "Source", "Target", "Retract 1", "Retract 2"
]


def map_action_to_location(action_value):
    if action_value < 16:
        return pylos.Location(0, int(action_value / 4), action_value % 4)
    action_value -= 16
    if action_value < 9:
        return pylos.Location(1, int(action_value / 3), action_value % 3)
    action_value -= 9
    if action_value < 4:
        return pylos.Location(2, int(action_value / 2), action_value % 2)
    action_value -= 4
    if action_value == 0:
        return pylos.Location(3, 0, 0)
    return None


def map_location_to_action(location):
    if location.layer == 0:
        return location.row * 4 + location.col

    if location.layer == 1:
        return 16 + location.row * 3 + location.col

    if location.layer == 2:
        return 16 + 9 + location.row * 2 + location.col

    return 29


class PylosEnv(gym.Env):
    done: bool
    metadata = {}

    def __init__(self):
        self.pylos = Pylos()
        self.done = False

        self.reset()

        # each move consists of 31 possible values (0-29 meaning one of the board positions,
        # 30 meaning 'none' or 'reserve' depending on the current phase)
        # note that for the 'target' phase, 30 is never a valid value
        self.action_space = spaces.Discrete(31)

    def state_from_pylos(self):
        player_onehot = np.array([
            1 - self.pylos.current_player,
            self.pylos.current_player
        ])

        # game phase
        phase_onehot = np.array([
            1 if self.pylos.phase == pylos.PHASE_SOURCE_LOCATION else 0,
            1 if self.pylos.phase == pylos.PHASE_TARGET_LOCATION else 0,
            1 if self.pylos.phase == pylos.PHASE_RETRACT1 else 0,
            1 if self.pylos.phase == pylos.PHASE_RETRACT2 else 0
        ])

        # board (3 nodes per board position)
        board_vector = np.array([
            [1 if ball_owner is None else 0 for ball_owner in self.flat_board()],
            [1 if ball_owner == 0 else 0 for ball_owner in self.flat_board()],
            [1 if ball_owner == 1 else 0 for ball_owner in self.flat_board()]
        ]).flatten('F')

        return np.concatenate([player_onehot, phase_onehot, board_vector])

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

    def step(self, action):
        if self.done:
            print("WARNING: step called after done")
            return self.state_from_pylos(), 0, self.done, {'warning_step_after_done': True}

        location = map_action_to_location(action)

        if not self.pylos.is_valid_move(location):
            return self.create_invalid_move_step_response(location)

        player = self.pylos.current_player
        reserve_before = self.pylos.reserve[player]
        self.pylos.move(location)
        reserve_after = self.pylos.reserve[player]

        winner = self.pylos.get_winner()
        reward = 1
        reward += reserve_after - reserve_before

        if winner is not None:
            reward += 10
            self.done = True

        return self.state_from_pylos(), reward, self.done, {'phase': self.pylos.phase}

    def render(self):
        if self.pylos.winner is not  None:
            print(" *** Winner *** ", self.pylos.winner)
        print("Player: ", self.pylos.current_player)
        print("Phase: ", PHASE_NAMES[self.pylos.phase])
        print("\n".join([self._render_row(r) for r in range(4)]))

    def _render_row(self, row):
        layers = self.pylos.render().split("#")

        split_layers = [layer.split("/") for layer in layers]
        return "  ".join(([layer[row] if row < len(layer) else " " * (4 - row) for layer in split_layers]))

    def create_invalid_move_step_response(self, location):
        return self.state_from_pylos(), -10, self.done, {'invalid': location}

