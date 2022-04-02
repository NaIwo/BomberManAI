import torch
from torch import nn
import numpy as np
from typing import TypeVar


M = TypeVar('M', bound='Model')

class Model:
    def __init__(self, obs_space, num_outputs):
        self.model = nn.Sequential(
            nn.Linear(obs_space.shape[0], 50),
            nn.ReLU(),
            nn.Linear(50, 20),
            nn.ReLU(),
            nn.Linear(20, 10),
            nn.ReLU(),
            nn.Linear(10, num_outputs),
            nn.Softmax(dim=0)
        )

        self.num_parameters: int = 0
        for p in self.model.parameters():
            p.requires_grad = False
            self.num_parameters += np.prod(np.array(p.data.shape))

    @classmethod
    def from_weights(cls, obs_space, num_outputs, weights) -> M:
        model = cls(obs_space, num_outputs)
        idx: int = 0
        for param in model.model.parameters():
            layer_shape: np.ndarray = np.array(param.data.shape)
            length: int = int(np.prod(layer_shape))
            param.data = torch.from_numpy(weights[idx:idx + length].reshape(layer_shape)).float()
            idx += length
        return model

    def __call__(self, observation: np.ndarray) -> np.ndarray:
        with torch.no_grad():
            out: np.ndarray = self.model(torch.from_numpy(observation).float())
        return np.array(out)
