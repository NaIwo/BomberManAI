from bomberman.usage.manual_policy import run_manual_policy
from bomberman import raw_env
from naive import naive

from typing import Optional, Dict

human_player_idx: Optional[int] = None

properties: Dict = {
    'num_players': 4,
    'num_bombs': 3,
    'num_coins': 6
}


def env_creator():
    return raw_env(**properties, score_limit=10, iteration_limit=1000,
                   human_player_idx=human_player_idx)


if __name__ == "__main__":
    env = env_creator()
    env.reset()

    agents: Dict = dict()
    for agent_name in env.agents:
        agents[agent_name] = lambda obs: naive(obs, properties)

    run_manual_policy(environment=env, human_player_idx=human_player_idx, agents_policy=agents)
