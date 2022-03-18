from typing import List, Dict, Tuple, Optional
import numpy as np

from gym.spaces import Discrete, Box
from pettingzoo import ParallelEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils import parallel_to_aec

from game.bomberman_game import BomberManGame
from game.config import GameProperties


def env():
    environment = raw_env()
    # this wrapper helps error handling for discrete action spaces
    environment = wrappers.AssertOutOfBoundsWrapper(environment)
    # Provides a wide variety of helpful user errors
    # Strongly recommended
    environment = wrappers.OrderEnforcingWrapper(environment)
    return environment


def raw_env():
    environment = parallel_env()
    environment = parallel_to_aec(environment)
    return environment


class parallel_env(ParallelEnv):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "bomber_man_v0",
        "is_parallelizable": True,
        "render_fps": GameProperties.FPS.value,
    }

    def __init__(self, num_players: int = 3,
                 num_bombs: int = 12,
                 num_coins: int = 3,
                 score_limit: int = 7,
                 iteration_limit: int = 700):

        self.game: BomberManGame = BomberManGame(num_players=num_players,
                                                 num_bombs=num_bombs,
                                                 num_coins=num_coins,
                                                 score_limit=score_limit,
                                                 iteration_limit=iteration_limit)

        self.possible_agents: List[str] = self.game.players_names()
        self.agents: List[str] = self.possible_agents[:]
        self.agent_name_mapping: Dict = dict(zip(self.possible_agents, list(range(len(self.possible_agents)))))

        shape: Tuple = (self.game.get_number_of_features(),)
        self.observation_spaces: Dict = dict(
            zip(self.agents,
                [Box(low=-np.inf, high=np.inf, shape=shape, dtype=np.float32) for _ in self.possible_agents])
        )

        num_actions: int = self.game.get_number_of_possible_moves()
        self.action_spaces = dict(zip(self.agents, [Discrete(num_actions) for _ in enumerate(self.possible_agents)]))

    def observation_space(self, agent: str) -> Box:
        return self.observation_spaces[agent]

    def action_space(self, agent: str) -> Discrete:
        return self.action_spaces[agent]

    def render(self, mode="human") -> Optional[None]:
        return self.game.render(mode=mode)

    def close(self):
        self.game.close()

    def reset(self) -> Dict[np.ndarray]:
        self.agents = self.possible_agents[:]
        self.game.reset()
        return {
            agent: self.game.get_observations(self.agent_name_mapping[agent]) for agent in self.agents
        }

    def step(self, actions):
        #  TODO
        pass
