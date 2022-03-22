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

# Example. Change it for your purpose.
checkpoint_path = 'RL/ray_results/ bomberman/PPO/PPO_bomberman_46476_00000_0_2022-03-22_12-29-02/checkpoint_000840/checkpoint-840'
params_path = Path(checkpoint_path).parent.parent / "params.pkl"

ModelCatalog.register_custom_model("BomberModel", BomberModel)


def env_creator():
    return raw_env(num_players=1, num_bombs=12, num_coins=4, score_limit=7, iteration_limit=1000)


if __name__ == '__main__':
    env = env_creator()
    env_name = 'bomberman_v0'
    register_env(env_name, lambda config: PettingZooEnv(env_creator()))

    with open(params_path, "rb") as f:
        config = pickle.load(f)
        # num_workers not needed since we are not training
        del config['num_workers']
        del config['num_gpus']

    ray.init(num_cpus=8, num_gpus=1)
    PPOagent = PPOTrainer(env=env_name, config=config)
    PPOagent.restore(checkpoint_path)

    run_manual_policy(environment=env,
                      agents_policy=lambda obs: PPOagent.get_policy("policy_0").compute_single_action(obs)[0])
