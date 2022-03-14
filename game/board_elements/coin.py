import pygame

from game.config import CoinProperties
from .base_element import BaseElement


class Coin(BaseElement):
    def __init__(self, left: int, top: int):
        super().__init__()
        self.rect = pygame.Rect(left, top, CoinProperties.WIDTH.value, CoinProperties.HEIGHT.value)
        self.clamp_position()
        self.image = pygame.Surface([CoinProperties.WIDTH.value, CoinProperties.HEIGHT.value])
        self.image.fill(CoinProperties.COLOR.value)

