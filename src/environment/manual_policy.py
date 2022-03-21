import numpy as np
import pygame

from src.game.config import Move, MOVE_TO_NUMBER


class ManualPolicy:
    def __init__(self, env, agent_id: int = 0):

        self.env = env
        self.agent_id: int = agent_id
        self.agent: str = self.env.agents[self.agent_id]

        self.default_action: int = MOVE_TO_NUMBER[Move.NOT_MOVING]

    def __call__(self, observation: np.ndarray, agent: str) -> int:

        assert agent == self.agent, f'Manual Policy only applied to agent: {self.agent}, but got tag for {agent}.'

        action: int = self.default_action

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()

                elif event.key == pygame.K_BACKSPACE:
                    self.env.reset()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            action = MOVE_TO_NUMBER[Move.UP]
        if keys[pygame.K_s]:
            action = MOVE_TO_NUMBER[Move.DOWN]
        if keys[pygame.K_a]:
            action = MOVE_TO_NUMBER[Move.LEFT]
        if keys[pygame.K_d]:
            action = MOVE_TO_NUMBER[Move.RIGHT]

        return action
