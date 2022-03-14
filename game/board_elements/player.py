import pygame
from typing import Dict, Tuple

from game.config import PlayerProperties, Move, MOVE_DICT
from .base_element import BaseElement


class Player(BaseElement):
    def __init__(self, left: int, top: int, color: Tuple):
        super().__init__()
        self.rect = pygame.Rect(left, top, PlayerProperties.WIDTH.value, PlayerProperties.HEIGHT.value)
        self.clamp_position()
        self.score: int = 0
        self.image = pygame.Surface([PlayerProperties.WIDTH.value, PlayerProperties.HEIGHT.value])
        self.image.fill(color)

    def update(self, move: int) -> None:
        move_tuple: Tuple = MOVE_DICT[move].value * Move.SPEED.value
        self.rect.x += move_tuple[0]
        self.rect.y += move_tuple[1]
        self.clamp_position()
