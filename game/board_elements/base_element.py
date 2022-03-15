from pygame.sprite import Sprite
from typing import Tuple, List
import pygame

from game.config import PlayerProperties, Screen


class BaseElement(Sprite):
    def __init__(self, coordinates_tuple: Tuple, name: str, shape_properties: List, color: Tuple):
        super().__init__()
        self.name: str = name
        self.rect = pygame.Rect(*coordinates_tuple)
        self.clamp_position()
        self._update_properties(shape_properties, color)

    def _update_properties(self, shape_properties: List, color: Tuple):
        self.image = pygame.Surface(shape_properties)
        self.image.fill(color)

    def update(self, move: int = -1) -> None:
        pass

    def clamp_position(self) -> None:
        max_x: int = Screen.WIDTH.value - PlayerProperties.WIDTH.value
        max_y: int = Screen.HEIGHT.value - PlayerProperties.HEIGHT.value
        self.rect.x = max(min(max_x, self.rect.x), 0)
        self.rect.y = max(min(max_y, self.rect.y), 0)
