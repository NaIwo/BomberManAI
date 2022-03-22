from bomberman import parallel_env
from bomberman.training.RL.custom_model import BomberModel

from ray import tune
from ray.rllib.models import ModelCatalog
from ray.tune.registry import register_env
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray.rllib.policy.policy import PolicySpec
from ray import shutdown


def env_creator(args):
    return parallel_env(num_players=1, num_bombs=12, num_coins=4, score_limit=7, iteration_limit=1000)


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
        },
        "gamma": 0.99,
    }

    policies = {"policy_0": PolicySpec(None, observation_space, act_space, config)}
    policy_ids = list(policies.keys())

    tune.run(
        "PPO",
        name="PPO",
        stop={
            "timesteps_total": 5000000
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

            # 'use_critic': True,
            'use_gae': True,
            "lambda": 0.9,

            "gamma": .99,

            # "kl_coeff": 0.001,
            # "kl_target": 1000.,
            "clip_param": 0.4,
            'grad_clip': 40,
            "entropy_coeff": 0.1,
            'vf_loss_coeff': 0.25,

            "sgd_minibatch_size": 128,
            "num_sgd_iter": 10,  # epoc
            'rollout_fragment_length': 512,
            "train_batch_size": -1,
            'lr': 0.0001,

            # Method specific
            "multiagent": {
                "policies": policies,
                "policy_mapping_fn": (
                    lambda agent_id, episode, worker, **kwargs: policy_ids[0]),
            },
        },
    )
