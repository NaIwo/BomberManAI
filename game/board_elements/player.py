from typing import List, Tuple

from game.config import PlayerProperties, Move, MOVE_DICT
from .base_element import BaseElement


class Player(BaseElement):
    NAMESPACE: str = 'Player_{}'

    def __init__(self, left: int, top: int, color: Tuple, idx: int):
        self.score: int = 0
        coordinates_tuple: Tuple = (left, top, PlayerProperties.WIDTH.value, PlayerProperties.HEIGHT.value)
        shape_properties: List = [PlayerProperties.WIDTH.value, PlayerProperties.HEIGHT.value]
        super().__init__(coordinates_tuple, Player.NAMESPACE.format(idx), shape_properties, color)

    def update(self, move: int = -1) -> None:
        move_tuple: Tuple = MOVE_DICT[move].value
        self.rect.x += move_tuple[0] * Move.SPEED.value
        self.rect.y += move_tuple[1] * Move.SPEED.value
        self.clamp_position()
