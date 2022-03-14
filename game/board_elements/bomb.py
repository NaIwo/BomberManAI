import pygame
from typing import Tuple

from game.config import BombProperties, Move, Screen
from .base_element import BaseElement


class Bomb(BaseElement):
    def __init__(self, left: int, top: int):
        super().__init__()
        self.rect = pygame.Rect(left, top, BombProperties.WIDTH.value, BombProperties.HEIGHT.value)
        self.is_moving: bool = False
        self.time_to_explosion: int = BombProperties.EXPLOSION_TIME.value
        self.clamp_position()
        self.current_move: Move = Move.NOT_MOVING
        self.image = pygame.Surface([BombProperties.WIDTH.value, BombProperties.HEIGHT.value])
        self.image.fill(BombProperties.COLOR.value)

    def update(self, player_move: Move) -> None:
        move_tuple: Tuple = player_move.value * Move.SPEED.value
        self.rect.x += move_tuple[0]
        self.rect.y += move_tuple[1]
        self.is_moving = True
        self.clamp_position()

    def clamp_position(self) -> None:
        max_x: int = Screen.WIDTH.value - BombProperties.WIDTH.value
        max_y: int = Screen.HEIGHT.value - BombProperties.HEIGHT.value
        new_x = max(min(max_x, self.rect.x), 0)
        new_y = max(min(max_y, self.rect.y), 0)
        if self.rect.x != new_x or self.rect.y != new_y:
            self.is_moving = False
        self.rect.x, self.rect.y = new_x, new_y
