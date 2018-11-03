from dqn.agent import Agent
from dqn.train import train_agents_and_save


def demo():
    agents = (Agent(), Agent())

    train_agents_and_save(agents)