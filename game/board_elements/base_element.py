from pygame.sprite import Sprite
from typing import Tuple, List, Optional
import pygame
import numpy as np

from game.config import GameProperties, PlayerProperties, Screen, MOVE_DICT_REVERSE, Move
from game.utils import get_image


class BaseElement(Sprite):
    def __init__(self, coordinates_tuple: Tuple, name: str, shape_properties: List, color: Tuple, image_path: str):
        super().__init__()
        self.current_move: Move = Move.NOT_MOVING
        self.name: str = name
        self.idx: int = int(self.name[self.name.rfind('_') + 1:])
        self._update_properties(coordinates_tuple, shape_properties, color)
        if GameProperties.LOAD_IMAGES.value:
            self.image: Optional[pygame.Surface] = get_image(image_path, self.rect.width, self.rect.height)
        self.clamp_position()

    def _update_properties(self, coordinates_tuple, shape_properties: List, color: Tuple):
        self.rect = pygame.Rect(*coordinates_tuple)
        self.image = pygame.Surface(shape_properties)
        self.image.fill(color)

    def _update_image(self, image_path: str) -> None:
        if GameProperties.LOAD_IMAGES.value:
            self.image: Optional[pygame.Surface] = get_image(image_path,  self.rect.width, self.rect.height)

    def update(self) -> None:
        pass

    def clamp_position(self) -> None:
        max_x: int = Screen.WIDTH.value - PlayerProperties.WIDTH.value
        max_y: int = Screen.HEIGHT.value - PlayerProperties.HEIGHT.value
        self.rect.x = max(min(max_x, self.rect.x), 0)
        self.rect.y = max(min(max_y, self.rect.y), 0)

    def get_current_move(self) -> np.ndarray:
        return np.eye(Move.NUMBER_OF_MOVES.value + 1)[MOVE_DICT_REVERSE[self.current_move]+1]

    def __eq__(self, other) -> bool:
        return self.name == other.name

    def __hash__(self):
        return self.idx
