import pygame

from src import bomberman


def random_simulation() -> None:
    max_cycles: int = 300
    parallel_env = bomberman.parallel_env(iteration_limit=max_cycles, num_players=4)
    parallel_env.reset()

    clock = pygame.time.Clock()
    for step in range(max_cycles):
        clock.tick(parallel_env.metadata['render.fps'])
        actions = {agent: parallel_env.action_space(agent).sample() for agent in parallel_env.agents}
        _ = parallel_env.step(actions)
        parallel_env.render()
    parallel_env.close()


if __name__ == '__main__':
    random_simulation()
