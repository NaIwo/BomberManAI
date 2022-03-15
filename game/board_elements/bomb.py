from typing import Tuple, List

from game.config import BombProperties, Move, Screen, MOVE_DICT, MOVE_DICT_REVERSE
from .base_element import BaseElement


class Bomb(BaseElement):
    NAMESPACE: str = 'Bomb_{}'

    def __init__(self, left: int, top: int, idx: int):
        self.time_to_explosion: int = BombProperties.TIME_TO_EXPLOSION.value
        self.current_move: Move = Move.NOT_MOVING
        self.speed: int = 0
        self.touched: bool = False
        coordinates_tuple: Tuple = (left, top, BombProperties.WIDTH.value, BombProperties.HEIGHT.value)
        shape_properties: List = [BombProperties.WIDTH.value, BombProperties.HEIGHT.value]
        super().__init__(coordinates_tuple, Bomb.NAMESPACE.format(idx), shape_properties,
                         color=BombProperties.COLOR.value)

    def update_move_information(self, move: int) -> None:
        if MOVE_DICT[move] != Move.NOT_MOVING:
            self.touched = True
            self.current_move = MOVE_DICT[move]
            self.speed = Move.SPEED.value
        else:
            new_move: int = (MOVE_DICT_REVERSE[self.current_move] + 2) % Move.NUMBER_OF_MOVES.value
            self.current_move = MOVE_DICT[new_move]

    def update(self, *kwargs) -> None:
        self.speed = max(self.speed + BombProperties.SLOWING_FACTOR.value, 0)
        self._update_explosion_information()
        if self.speed == 0:
            return
        self.rect.x += self.current_move.value[0] * self.speed
        self.rect.y += self.current_move.value[1] * self.speed
        self.clamp_position()

    def _update_explosion_information(self) -> None:
        if not self.touched:
            return
        if self.time_to_explosion == 0:
            self.rect.x = max(self.rect.centerx - (BombProperties.EXPLOSION_WIDTH.value / 2), 0)
            self.rect.y = max(self.rect.centery - (BombProperties.EXPLOSION_HEIGHT.value / 2), 0)
            shape_properties: List = [BombProperties.EXPLOSION_WIDTH.value, BombProperties.EXPLOSION_HEIGHT.value]
            self._update_properties(shape_properties, BombProperties.EXPLOSION_COLOR.value)
        self.time_to_explosion = max(self.time_to_explosion - 1, -BombProperties.EXPLOSION_TIME.value)

    def clamp_position(self) -> None:
        max_x: int = Screen.WIDTH.value - BombProperties.WIDTH.value
        max_y: int = Screen.HEIGHT.value - BombProperties.HEIGHT.value
        new_x = max(min(max_x, self.rect.x), 0)
        new_y = max(min(max_y, self.rect.y), 0)
        if self.rect.x != new_x or self.rect.y != new_y:
            new_move: int = (MOVE_DICT_REVERSE[self.current_move] + 2) % Move.NUMBER_OF_MOVES.value
            self.current_move = MOVE_DICT[new_move]
        self.rect.x, self.rect.y = new_x, new_y
