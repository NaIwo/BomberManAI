import pygame

from bomberman import parallel_env


def run_random_simulation() -> None:
    max_cycles: int = 300
    parallel_environment = parallel_env(iteration_limit=max_cycles, num_players=4)
    parallel_environment.reset()

    clock = pygame.time.Clock()
    for step in range(max_cycles):
        clock.tick(parallel_environment.metadata['render.fps'])
        actions = {agent: parallel_environment.action_space(agent).sample() for agent in parallel_environment.agents}
        _ = parallel_environment.step(actions)
        parallel_environment.render()
    parallel_environment.close()


if __name__ == '__main__':
    run_random_simulation()
