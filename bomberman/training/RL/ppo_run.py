from bomberman.usage.manual_policy import run_manual_policy
from bomberman import raw_env
from bomberman.training.RL.custom_model import BomberModel

import ray
from ray.tune.registry import register_env
from ray.rllib.agents.ppo import PPOTrainer
from ray.rllib.env.wrappers.pettingzoo_env import PettingZooEnv
from ray.rllib.models import ModelCatalog
from pathlib import Path
import pickle5 as pickle
from typing import Optional, Dict

# Example. Change it for your purpose.
checkpoint_path_1 = 'RL/ray_results/ bomberman/PPO/4_3_3_with_random_new_obs/checkpoint_000300/checkpoint-300'
params_path_1 = Path(checkpoint_path_1).parent.parent / "params.pkl"

checkpoint_path_2 = 'RL/ray_results/ bomberman/PPO/4_3_3_with_random_new_obs/checkpoint_000110/checkpoint-110'
params_path_2 = Path(checkpoint_path_1).parent.parent / "params.pkl"

ModelCatalog.register_custom_model("BomberModel", BomberModel)

human_player_idx: Optional[int] = None


def env_creator():
    return raw_env(num_players=4, num_bombs=3, num_coins=6, score_limit=10, iteration_limit=1000,
                   human_player_idx=human_player_idx)


def load_agent(params_path: Path, checkpoint_path: str) -> PPOTrainer:
    with open(params_path, "rb") as f:
        config = pickle.load(f)
        # num_workers not needed since we are not training
        del config['num_workers']
        del config['num_gpus']

    PPOagent = PPOTrainer(env=env_name, config=config)
    PPOagent.restore(checkpoint_path)
    return PPOagent


if __name__ == '__main__':
    env = env_creator()
    env.reset()

    env_name = 'bomberman_v0'
    register_env(env_name, lambda config: PettingZooEnv(env_creator()))
    ray.init(num_cpus=8, num_gpus=1)

    agent_1 = load_agent(params_path_1, checkpoint_path_1)
    agent_2 = load_agent(params_path_2, checkpoint_path_2)
    agents: Dict = {
        env.agents[0]: lambda obs: agent_1.get_policy("learning_policy").compute_single_action(obs)[0],
        env.agents[1]: lambda obs: agent_2.get_policy("learning_policy").compute_single_action(obs)[0],
        env.agents[2]: lambda obs: agent_1.get_policy("learning_policy").compute_single_action(obs)[0],
        env.agents[3]: lambda obs: agent_2.get_policy("learning_policy").compute_single_action(obs)[0]
    }

    run_manual_policy(environment=env, human_player_idx=human_player_idx, agents_policy=agents)
