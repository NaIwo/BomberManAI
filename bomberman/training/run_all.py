from bomberman.usage.manual_policy import run_manual_policy
from bomberman import raw_env
from bomberman.training.RL.custom_model import BomberModel
from naive.naive import naive
from evolution.model import Model

import ray
from ray.tune.registry import register_env
from ray.rllib.agents.ppo import PPOTrainer
from ray.rllib.env.wrappers.pettingzoo_env import PettingZooEnv
from ray.rllib.models import ModelCatalog
from pathlib import Path
import pickle5 as pickle
from typing import Optional, Dict
import os
import numpy as np

# Example. Change it for your purpose.
ppo_checkpoint_path = 'RL/ray_results/ bomberman/PPO/4_3_3_with_random_new_obs/checkpoint_000300/checkpoint-300'
ppo_params_path = Path(ppo_checkpoint_path).parent.parent / "params.pkl"

cma_checkpoint_path = os.path.join('.', 'evolution', 'CMA', '20220403-142851', 'weights.npy')

ModelCatalog.register_custom_model("BomberModel", BomberModel)

human_player_idx: Optional[int] = None

properties: Dict = {
    'num_players': 4,
    'num_bombs': 3,
    'num_coins': 6
}


def env_creator():
    return raw_env(**properties, score_limit=10, iteration_limit=1000,
                   human_player_idx=human_player_idx)


def get_ppo_agent(params_path: Path, checkpoint_path: str) -> PPOTrainer:
    env_name = 'bomberman_v0'
    register_env(env_name, lambda config: PettingZooEnv(env_creator()))
    ray.init(num_cpus=8, num_gpus=1)
    with open(params_path, "rb") as f:
        config = pickle.load(f)
        # num_workers not needed since we are not training
        del config['num_workers']
        del config['num_gpus']

    PPOagent = PPOTrainer(env=env_name, config=config)
    PPOagent.restore(checkpoint_path)
    return PPOagent


def get_cma_agent() -> Model:
    weights: np.ndarray = np.load(cma_checkpoint_path)
    observation_space = env.observation_space(env.agents[0])
    act_space = env.action_space(env.agents[0])
    return Model.from_weights(observation_space, act_space.n, weights)


if __name__ == '__main__':
    env = env_creator()
    env.reset()

    ppo_agent = get_ppo_agent(ppo_params_path, ppo_checkpoint_path)
    cma_agent: Model = get_cma_agent()

    agents: Dict = {
        env.agents[0]: lambda obs: np.argmax(cma_agent(obs)),
        env.agents[1]: lambda obs: ppo_agent.get_policy("learning_policy").compute_single_action(obs)[0],
        env.agents[2]: lambda obs: naive(obs, properties),
        env.agents[3]: lambda _: env.action_space(env.agents[3]).sample()
    }

    run_manual_policy(environment=env, human_player_idx=human_player_idx, agents_policy=agents)
