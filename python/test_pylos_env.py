import gym
import gym.spaces
from nose.tools import assert_is_not_none, assert_equal
import pylos_env
from pylos import Location
import numpy as np
from numpy.testing import assert_array_equal


def test_sanity():
    assert_is_not_none(gym)
    assert_is_not_none(pylos_env)


def test_make_env():
    env = gym.envs.make('Pylos-v0')

    assert_is_not_none(env)


def test_reset_env():
    env = gym.envs.make('Pylos-v0')

    state = env.reset()

    assert_current_player(state, 0)
    assert_game_phase(state, 0)
    assert_board(state, "..../..../..../....#.../.../...#../..#.")


def test_take_ball_from_reserve():
    env = gym.envs.make('Pylos-v0')

    env.reset()
    state, reward, done, info = env.step(30)

    assert_current_player(state, 0)
    assert_game_phase(state, 1)
    assert_board(state, "..../..../..../....#.../.../...#../..#.")


def assert_game_phase(state, phase):
    if phase == 0:
        assert_array_equal(state[2:6], np.array([1, 0, 0, 0]))
    if phase == 1:
        assert_array_equal(state[2:6], np.array([0, 1, 0, 0]))
    if phase == 2:
        assert_array_equal(state[2:6], np.array([0, 0, 1, 0]))
    if phase == 3:
        assert_array_equal(state[2:6], np.array([0, 0, 0, 1]))


def test_first_move():
    env = gym.envs.make('Pylos-v0')
    env.reset()

    # source
    state, reward, done, info = env.step(30)
    assert_current_player(state, 0)
    assert_game_phase(state, 1)
    assert_board(state, "..../..../..../....#.../.../...#../..#.")
    assert_equal(reward, 0)
    assert not done

    # target
    state, reward, done, info = env.step(0)
    assert_current_player(state, 0)
    assert_game_phase(state, 2)
    assert_board(state, "0.../..../..../....#.../.../...#../..#.")
    assert_equal(reward, 0)
    assert not done

    # retract 1
    state, reward, done, info = env.step(30)
    assert_current_player(state, 0)
    assert_game_phase(state, 3)
    assert_board(state, "0.../..../..../....#.../.../...#../..#.")
    assert_equal(reward, 0)
    assert not done

    # retract 2
    state, reward, done, info = env.step(30)
    assert_current_player(state, 1)
    assert_game_phase(state, 0)
    assert_board(state, "0.../..../..../....#.../.../...#../..#.")
    assert_equal(reward, 0)
    assert not done


def test_two_moves():
    env = gym.envs.make('Pylos-v0')
    env.reset()

    # player 1
    env.step(30)
    env.step(0)
    env.step(30)
    state, reward, done, info = env.step(30)

    assert_current_player(state, 1)
    assert_game_phase(state, 0)
    assert_board(state, "0.../..../..../....#.../.../...#../..#.")
    assert_equal(reward, 0)
    assert not done

    # player 2 source
    state, reward, done, info = env.step(30)
    assert_current_player(state, 1)
    assert_game_phase(state, 1)
    assert_board(state, "0.../..../..../....#.../.../...#../..#.")
    assert_equal(reward, 0)
    assert not done

    # player 2 target
    state, reward, done, info = env.step(1)
    assert_current_player(state, 1)
    assert_game_phase(state, 2)
    assert_board(state, "01../..../..../....#.../.../...#../..#.")
    assert_equal(reward, 0)
    assert not done

    # player 2 retract 1
    state, reward, done, info = env.step(30)
    assert_current_player(state, 1)
    assert_game_phase(state, 3)
    assert_board(state, "01../..../..../....#.../.../...#../..#.")
    assert_equal(reward, 0)
    assert not done

    # player 2 retract 2
    state, reward, done, info = env.step(30)
    assert_current_player(state, 0)
    assert_game_phase(state, 0)
    assert_board(state, "01../..../..../....#.../.../...#../..#.")
    assert_equal(reward, 0)
    assert not done


def test_invalid_move_negative_reward():
    env = gym.envs.make('Pylos-v0')
    state, reward, done, info = env.step(0)
    assert_current_player(state, 0)
    assert_game_phase(state, 0)
    assert_board(state, "..../..../..../....#.../.../...#../..#.")
    assert not done
    assert_equal(reward, -1)
    assert_equal(info, {'invalid': Location(0, 0, 0)})


def test_win_reward():
    env = gym.envs.make('Pylos-v0')
    env.reset()

    for i in range(30):
        env.step(30)
        env.step(i)
        env.step(30)
        state, reward, done, info = env.step(30)

    assert_current_player(state, 0)
    assert_game_phase(state, 0)
    assert_board(state, "0101/0101/0101/0101#010/101/010#10/10#1")
    assert done
    assert_equal(reward, 10)


def test_invalid_move_to_top():
    env = gym.envs.make('Pylos-v0')

    env.step(30)
    state, reward, done, info = env.step(29)

    assert_equal(reward, -1)


def assert_current_player(state, expected):
    assert_array_equal(state[:2], np.array([1, 0] if expected == 0 else [0, 1]))


def assert_board(state, expected):
    actual = layers_from_state(state[6:])
    assert_equal(render_layers(actual), expected)


def layers_from_state(state):
    layers = [[[None for c in range(size)] for r in range(size)] for size in [4, 3, 2, 1]]

    for layer in range(4):
        for r in range(4 - layer):
            for c in range(4 - layer):
                idx = get_location_idx(layer, r, c)
                pos = np.argmax(state[idx:idx + 3])
                layers[layer][r][c] = [None, 0, 1][pos]

    return layers


def get_location_idx(layer, row, col):
    if layer == 0:
        return 3 * (row * 4 + col)
    if layer == 1:
        return 3 * (16 + row * 3 + col)
    if layer == 2:
        return 3 * (16 + 9 + row * 2 + col)
    return 3 * (16 + 9 + 4)


def render_layers(layers):
    return "#".join(["/".join(["".join([str(c) if c is not None else "." for c in r]) for r in l]) for l in layers])
