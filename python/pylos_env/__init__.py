from gym.envs.registration import register

register(
    id='Pylos-v0',
    entry_point='pylos_env.envs:PylosEnv',
)
