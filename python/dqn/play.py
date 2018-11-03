import gym
from pylos_env.tools import print_human
from pylos_env.envs import map_location_to_action
from pylos import Location


def play_game(agent0):
    env = gym.envs.make('Pylos-v0')

    state = env.reset()
    done = False
    while not done:
        print("   AGENT")
        print_human(env)
        state, reward, done, info = agent_turn(agent0, env, state)

        print("   PLAYER")
        print_human(env)
        state, reward, done, info = player_turn(env)


def self_play(agents):
    env = gym.envs.make('Pylos-v0')

    done = False
    state = env.reset()

    while not done:
        for i in range(4):
            current_player = state[1]
            agent = agents[current_player]
            action = agent.choose_action(state, explore=False)
            state, reward, done, info = env.step(action)
            print(info)

        print_human(env)


def agent_turn(agent, env, state):
    # TODO: correct for invalid moves!
    state, reward, done, info = env.step(agent.choose_action(state))
    state, reward, done, info = env.step(agent.choose_action(state))
    state, reward, done, info = env.step(agent.choose_action(state))
    return env.step(agent.choose_action(state))


def player_turn(env):
    src = get_move_action("source layer row col?")
    state, reward, done, info = env.step(src)

    target = get_move_action("target layer row col?")
    state, reward, done, info = env.step(target)

    r1 = get_move_action("retract1 layer row col?")
    state, reward, done, info = env.step(r1)

    r2 = get_move_action("retract2 layer row col?")
    return env.step(r2)


def get_move_action(prompt):
    move = input(prompt)
    if move.strip() == "":
        return 30

    location = Location([int(c) for c in move.split(" ")])
    return map_location_to_action(location)
