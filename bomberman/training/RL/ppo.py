from bomberman import parallel_env
from bomberman.training.RL.custom_model import BomberModel

from ray import tune
from ray.rllib.models import ModelCatalog
from ray.tune.registry import register_env
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray.rllib.policy.policy import PolicySpec
from ray.rllib.examples.policy.random_policy import RandomPolicy
from ray import shutdown
import random


def env_creator(args):
    return parallel_env(num_players=4, num_bombs=3, num_coins=6, score_limit=10, iteration_limit=1000)


if __name__ == "__main__":
    shutdown()

    env_name = "bomberman"

    register_env(env_name, lambda config: ParallelPettingZooEnv(env_creator(config)))

    env = ParallelPettingZooEnv(env_creator({}))
    observation_space = env.observation_space
    act_space = env.action_space

    ModelCatalog.register_custom_model("BomberModel", BomberModel)

    config = {
        "model": {
            "custom_model": "BomberModel",
        }
    }


    def policy_mapping_fn(agent_id, episode, worker, **kwargs):
        # agent_idx = int(agent_id[-1])
        # return "learning_policy" if episode.episode_id % 2 == agent_idx % 2 else "random_policy"
        return random.sample(["learning_policy", "random_policy"], 1)[0]


    policies = {
        "learning_policy": PolicySpec(None, observation_space, act_space, config),
        "random_policy": PolicySpec(policy_class=RandomPolicy)
    }

    tune.run(
        "PPO",
        name="PPO",
        stop={
            "timesteps_total": 15_000_000
        },
        checkpoint_freq=10,
        local_dir="./ray_results/ " + env_name,
        config={
            # Environment specific
            "env": env_name,
            # General
            "log_level": "ERROR",
            "framework": "torch",
            "num_gpus": 1,
            "num_workers": 6,
            "num_envs_per_worker": 1,
            "compress_observations": False,
            "batch_mode": 'truncate_episodes',

            'lr': 0.0002,
            'lambda': 0.90,
            'gamma': 0.99,
            'sgd_minibatch_size': 512,
            'train_batch_size': 4000,
            # 'clip_param': 0.2,
            # For running in editor, just use one Worker (we only have
            # one Unity running)!
            'num_sgd_iter': 20,
            'rollout_fragment_length': 200,
            'no_done_at_end': True,
            'evaluation_interval': 0,
            'evaluation_num_episodes': 1,

            # Method specific
            "multiagent": {
                "policies": policies,
                "policy_mapping_fn": policy_mapping_fn,
                "policies_to_train": ["learning_policy"]
            }
        }
    )
