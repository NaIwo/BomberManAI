import pygame
from typing import Union, Dict, Callable, Optional

from bomberman import ManualPolicy, raw_env


def run_manual_policy(environment=None, agents_policy: Union[Dict[str, Callable], Callable, None] = None,
                      human_player_idx: Optional[int] = 0) -> None:
    FPS: int = 125
    clock = pygame.time.Clock()

    env = environment if environment is not None else raw_env(human_player_idx=human_player_idx, iteration_limit=1100)
    env.reset()

    manual_policy = ManualPolicy(env)

    for agent in env.agent_iter():
        clock.tick(FPS)

        observation, reward, done, info = env.last()

        if done:
            env.reset()

        if agent == manual_policy.agent and human_player_idx is not None:
            action = manual_policy(observation, agent)
        else:
            if agents_policy is None:
                action = env.action_space(agent).sample()
            elif isinstance(agents_policy, dict):
                action = agents_policy[agent](observation)
            else:
                action = agents_policy(observation)

        env.step(action)

        env.render()

        manual_policy.check_for_special_actions(env)


if __name__ == '__main__':
    run_manual_policy()
