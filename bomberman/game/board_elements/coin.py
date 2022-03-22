from typing import Tuple, List

from bomberman.game.config import CoinProperties
from .base_element import BaseElement


class Coin(BaseElement):
    NAMESPACE: str = 'Bomb_{}'

    def __init__(self, left: int, top: int, idx: int):
        coordinates_tuple: Tuple = (left, top, CoinProperties.WIDTH.value, CoinProperties.HEIGHT.value)
        shape_properties: List = [CoinProperties.WIDTH.value, CoinProperties.HEIGHT.value]
        super().__init__(coordinates_tuple, Coin.NAMESPACE.format(idx), shape_properties,
                         color=CoinProperties.COLOR.value, image_path=CoinProperties.IMAGE_PATH.value)
        self.destroyed_by_bomb: bool = False
        self.collected_by_player: bool = False

    def update(self) -> None:
        if self._should_be_killed():
            self.kill()

    def _should_be_killed(self) -> bool:
        return self.destroyed_by_bomb or self.collected_by_player

