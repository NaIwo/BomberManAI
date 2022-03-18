import pygame

import bomberman


def random_simulation() -> None:
    max_cycles = 5000
    parallel_env = bomberman.parallel_env(iteration_limit=max_cycles, num_players=4)
    observations = parallel_env.reset()

    clock = pygame.time.Clock()
    for step in range(max_cycles):
        clock.tick(parallel_env.metadata['render.fps'])
        actions = {agent: parallel_env.action_space(agent).sample() for agent in parallel_env.agents}
        observations, rewards, dones, infos = parallel_env.step(actions)
        parallel_env.render()
    parallel_env.close()


def manual_policy() -> None:
    clock = pygame.time.Clock()

    env = bomberman.raw_env(human_player_idx=0, iteration_limit=100)
    env.reset()

    manual_policy = bomberman.ManualPolicy(env)

    for agent in env.agent_iter():
        clock.tick(env.metadata['render.fps'])

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
    # random_simulation()
    # bomberman.manual_control()
    manual_policy()
