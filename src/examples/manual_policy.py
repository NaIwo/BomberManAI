import pygame

from src import bomberman


def manual_policy() -> None:
    FPS: int = 85
    clock = pygame.time.Clock()

    env = bomberman.raw_env(human_player_idx=0, iteration_limit=300)
    env.reset()

    manual_policy = bomberman.ManualPolicy(env)

    for agent in env.agent_iter():
        clock.tick(FPS)

        observation, reward, done, info = env.last()

        if done:
            env.reset()

        if agent == manual_policy.agent:
            action = manual_policy(observation, agent)
        else:
            action = env.action_space(agent).sample()
        env.step(action)

        env.render()


if __name__ == '__main__':
    manual_policy()
