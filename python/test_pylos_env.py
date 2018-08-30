import gym
import gym.spaces
from nose.tools import assert_equal

def test_sanity():
    assert gym != None


def test_make_env():
    env = gym.envs.make('Pylos-v0')


def test_reset_env():
    env = gym.envs.make('Pylos-v0')

    state = env.reset()

    assert state['current_player'] == 0
    assert state['board'][0][0] == 0


def test_single_move():
    env = gym.envs.make('Pylos-v0')

    env.reset()
    state, reward, done, info = env.step([30, 0, 30, 30])

    assert state['current_player'] == 1
    assert reward == 0
    assert not done
    assert info == {}


def test_two_moves():
    env = gym.envs.make('Pylos-v0')
    env.reset()
    env.step((31, 0, 31, 31))

    state, reward, done, info = env.step((30, 1, 30, 30))

    assert state['current_player'] == 0
    assert reward == 0
    assert not done
    assert info == {}


def test_invalid_move():
    env = gym.envs.make('Pylos-v0')
    env.reset()
    env.step([30, 0, 30, 30])

    state, reward, done, info = env.step([30, 0, 30, 30])

    assert not done
    assert state['current_player'] == 0
    assert reward == 0
    assert info == {'invalid_move': True, 'alt_move': (None, (0, 0, 1))}


def test_win_reward():
    env = gym.envs.make('Pylos-v0')
    env.reset()

    for i in range(30):
        state, reward, done, info = env.step([30, 0, 30, 30])

    print(env.pylos.render())
    assert done
    assert reward == 1


def test_action_space():
    env = gym.envs.make('Pylos-v0')

    assert env.action_space.sample().shape == (4,)


def test_invalid_move_to_top():
    env = gym.envs.make('Pylos-v0')

    state, reward, done, info = env.step((30, 29, 30, 30))

    assert info == {'invalid_move': True, 'alt_move': (None, (0, 0, 0))}
