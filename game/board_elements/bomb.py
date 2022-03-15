from typing import Tuple, List

from game.config import BombProperties, Move, Screen, MOVE_DICT
from .base_element import BaseElement


class Bomb(BaseElement):
    NAMESPACE: str = 'Bomb_{}'

    def __init__(self, left: int, top: int, idx: int):
        coordinates_tuple: Tuple = (left, top, BombProperties.WIDTH.value, BombProperties.HEIGHT.value)
        shape_properties: List = [BombProperties.WIDTH.value, BombProperties.HEIGHT.value]
        super().__init__(coordinates_tuple, Bomb.NAMESPACE.format(idx), shape_properties, color=BombProperties.COLOR.value)
        self.is_moving: bool = False
        self.time_to_explosion: int = BombProperties.EXPLOSION_TIME.value
        self.current_move: Move = Move.NOT_MOVING

    def update(self, move: int = -1) -> None:
        if MOVE_DICT[move] != Move.NOT_MOVING:
            self.is_moving = True
            self.current_move = MOVE_DICT[move]
        self.rect.x += self.current_move.value[0] * Move.SPEED.value
        self.rect.y += self.current_move.value[1] * Move.SPEED.value
        self.clamp_position()

    def clamp_position(self) -> None:
        max_x: int = Screen.WIDTH.value - BombProperties.WIDTH.value
        max_y: int = Screen.HEIGHT.value - BombProperties.HEIGHT.value
        new_x = max(min(max_x, self.rect.x), 0)
        new_y = max(min(max_y, self.rect.y), 0)
        if self.rect.x != new_x or self.rect.y != new_y:
            self.is_moving = False
        self.rect.x, self.rect.y = new_x, new_y
