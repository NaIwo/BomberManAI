from typing import List, Dict, Tuple, Optional
import numpy as np

from gym.spaces import Discrete, Box
from pettingzoo import ParallelEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils import parallel_to_aec

from bomberman.game.bomberman_game import BomberManGame
from bomberman.game.config import GameProperties, Score, Screen


def env(**kwargs):
    environment = raw_env(**kwargs)
    # this wrapper helps error handling for discrete action spaces
    environment = wrappers.AssertOutOfBoundsWrapper(environment)
    # Provides a wide variety of helpful user errors
    # Strongly recommended
    environment = wrappers.OrderEnforcingWrapper(environment)
    return environment


def raw_env(**kwargs):
    environment = parallel_env(**kwargs)
    environment = parallel_to_aec(environment)
    return environment


class parallel_env(ParallelEnv):
    metadata = {
        "render.modes": ["human", "rgb_array"],
        "name": "bomber_man_v0",
        "is_parallelizable": True,
        "render.fps": GameProperties.FPS.value,
    }

    def __init__(self, num_players: int = GameProperties.NUM_PLAYERS.value,
                 num_bombs: int = GameProperties.NUM_BOMBS.value,
                 num_coins: int = GameProperties.NUM_COINS.value,
                 score_limit: int = Score.SCORE_LIMIT.value,
                 iteration_limit: Optional[int] = GameProperties.ITERATION_LIMIT.value,
                 human_player_idx: Optional[int] = None):

        self.game: BomberManGame = BomberManGame(num_players=num_players,
                                                 num_bombs=num_bombs,
                                                 num_coins=num_coins,
                                                 score_limit=score_limit,
                                                 iteration_limit=iteration_limit,
                                                 human_player_idx=human_player_idx)

        self.possible_agents: List[str] = self.game.players_names()
        self.agents: List[str] = self.possible_agents[:]
        self.agent_name_mapping: Dict = dict(zip(self.possible_agents, list(range(len(self.possible_agents)))))

        shape: Tuple = self.game.get_observations_shape()
        self.observation_spaces: Dict = dict(
            zip(self.agents,
                [Box(low=0, high=1, shape=shape, dtype=np.float32) for _ in self.possible_agents])
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

    def reset(self) -> Dict[str, np.ndarray]:
        self.agents = self.possible_agents[:]
        self.game.reset()
        return {
            agent: self.game.get_observations(self.agent_name_mapping[agent]) for agent in self.agents
        }

    def step(self, actions: Dict) -> Tuple:
        if not actions:
            self.agents = []
            return {}, {}, {}, {}

        rewards: Dict = dict()
        observations: Dict = dict()
        dones: Dict = dict()
        infos: Dict = dict()

        agent_name: str
        action: int
        for agent_name, action in actions.items():
            rewards[agent_name] = self.game.perform_action_and_get_reward(self.agent_name_mapping[agent_name], action)

        """
        Very important to remember update the state.
        """
        self.game.update()

        env_done: bool = self.game.is_end_game()
        winners_list: List[int] = self.game.get_winners_idx()

        agent_idx: int
        agent_name: int
        for agent_idx, agent_name in enumerate(self.agents):
            observations[agent_name] = self.game.get_observations(agent_idx=agent_idx)
            dones[agent_name] = env_done
            infos[agent_name] = {}
            # rewards[agent_name] += (env_done * self.game.score_limit) * (1 if agent_idx in winners_list else -1)

        if env_done:
            self.agents = []
        return observations, rewards, dones, infos
