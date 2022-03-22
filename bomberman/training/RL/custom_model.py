from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from torch import nn


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
