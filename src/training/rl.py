from src import bomberman

from ray import tune
from ray.rllib.models import ModelCatalog
from ray.tune.registry import register_env
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray import shutdown
from torch import nn
from typing import Tuple


class BomberModel(TorchModelV2, nn.Module):
    def __init__(self, obs_space, action_space, num_outputs, *args, **kwargs):
        TorchModelV2.__init__(self, obs_space, action_space, num_outputs, *args, **kwargs)
        nn.Module.__init__(self)
        self.model = nn.Sequential(
            nn.BatchNorm1d(obs_space.shape[0]),
            nn.Linear(obs_space.shape[0], 100),
            nn.ReLU(),
            nn.BatchNorm1d(100),
            nn.Linear(100, 50),
            nn.ReLU(),
            nn.BatchNorm1d(50),
            nn.Linear(50, 20),
            nn.ReLU(),
        )
        self.policy_fn = nn.Linear(20, num_outputs)
        self.value_fn = nn.Linear(20, 1)

    def forward(self, input_dict, state, seq_lens):
        self._query_model(input_dict)
        return self.policy_fn(self.current_model_out), state

    def value_function(self):
        return self.value_fn(self.current_model_out).flatten()

    def _query_model(self, input_dict):
        self.current_model_out = self.model(input_dict["obs"])


def env_creator(args):
    return bomberman.parallel_env(num_players=4, num_bombs=12, num_coins=4, score_limit=7, iteration_limit=1000)


if __name__ == "__main__":
    shutdown()

    env_name = "bomberman"

    register_env(env_name, lambda config: ParallelPettingZooEnv(env_creator(config)))

    env = ParallelPettingZooEnv(env_creator({}))
    observation_space = env.observation_space
    act_space = env.action_space

    ModelCatalog.register_custom_model("BomberModel", BomberModel)


    def gen_policy() -> Tuple:
        config = {
            "model": {
                "custom_model": "BomberModel",
            },
            "gamma": 0.99,
        }
        return None, observation_space, act_space, config


    policies = {"policy_0": gen_policy()}

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

            "sgd_minibatch_size": 64,
            "num_sgd_iter": 10,  # epoc
            'rollout_fragment_length': 512,
            "train_batch_size": -1,
            'lr': 0.0001,

            # Method specific
            "multiagent": {
                "policies": policies,
                "policy_mapping_fn": (
                    lambda agent_id: policy_ids[0]),
            },
        },
    )
