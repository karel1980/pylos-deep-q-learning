from collections import Iterable
from typing import Tuple
from dqn.agent import Agent
import gym
import random


def play_game_and_train(env, agents, exploration_rate):
    memories = get_game_experience(env, agents, exploration_rate)
    agents[0].remember(memories[0])
    agents[0].remember(memories[1])
    return len(memories[0]) + len(memories[1])


def get_game_experience(env, agents, exploration_rate):
    memories: Tuple[Iterable[Tuple]] = ([], [])
    state = env.reset()

    done = False
    moves = 0
    while not done and moves < 10000:
        moves += 1
        current_player = get_current_player(state)
        current_player_memory = memories[current_player]
        current_agent = agents[current_player]

        if random.random() <= exploration_rate:
            action = env.action_space.sample()
        else:
            action = current_agent.choose_action(state)

        next_state, reward, done, info = env.step(action)

        current_player_memory.append((state, action, next_state, reward, done))
        state = next_state

    if not done:
        print("Game did not end after 10000 moves")

    return memories


def get_current_player(state):
    return state[1]


def load_agents():
    agents = (Agent(), Agent())
    agents[0].model.load_weights('agent0.weights')
    agents[1].model.load_weights('agent1.weights')


def train_agents_and_save(agents):
    env = gym.envs.make('Pylos-v0')
    exploration_rate = 0.9
    for i in range(1000):
        num_moves = play_game_and_train(env, agents, exploration_rate)
        print("%d / 1000 --    exp: %.2f  -- moves: %5d" % (i, exploration_rate, num_moves))
        if i % 10 == 0:
            print("saving models")
            agents[0].model.save_weights('agent0.weights')
            agents[1].model.save_weights('agent1.weights')

        if exploration_rate > 0.05:
            exploration_rate -= 0.01


def evaluate_win_rate(agents):
    env = gym.envs.make('Pylos-v0')
    wins = [0, 0]
    for i in range(100):
        get_game_experience(env, agents)
        wins[env.pylos.winner] += 1
