import numpy as np

from bomberman.usage.manual_policy import run_manual_policy
from bomberman import raw_env
from bomberman.training.evolution.model import Model


from typing import Optional, Dict
import os

# Example. Change it for your purpose.
checkpoint_path = os.path.join('.', 'CMA', '20220403-185817', 'weights.npy')

human_player_idx: Optional[int] = None


def env_creator():
    return raw_env(num_players=4, num_bombs=3, num_coins=6, score_limit=10, iteration_limit=1000,
                   human_player_idx=human_player_idx)


if __name__ == '__main__':
    env = env_creator()
    env.reset()
    observation_space = env.observation_space(env.agents[0])
    act_space = env.action_space(env.agents[0])
    weights: np.ndarray = np.load(checkpoint_path)
    model: Model = Model.from_weights(observation_space, act_space.n, weights)

    agents: Dict = dict()
    for agent_name in env.agents:
        agents[agent_name] = lambda obs: np.argmax(model(obs))

    run_manual_policy(environment=env, human_player_idx=human_player_idx, agents_policy=agents)
