import pygame
from typing import Tuple, List

from game.config import CoinProperties
from .base_element import BaseElement


class Coin(BaseElement):
    NAMESPACE: str = 'Bomb_{}'

    def __init__(self, left: int, top: int, idx: int):
        coordinates_tuple: Tuple = (left, top, CoinProperties.WIDTH.value, CoinProperties.HEIGHT.value)
        shape_properties: List = [CoinProperties.WIDTH.value, CoinProperties.HEIGHT.value]
        super().__init__(coordinates_tuple, Coin.NAMESPACE.format(idx), shape_properties,
                         color=CoinProperties.COLOR.value)
