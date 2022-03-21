import random
from typing import Tuple, List, Optional
import numpy as np
import pygame
import os
from functools import lru_cache

from .config import Screen, GameProperties, PlayerProperties


class GenerationError(Exception):
    pass


class RandomValues:
    @staticmethod
    def get_x_y_without_overlapping(points: List) -> Tuple:
        rep: int = 0
        points: np.ndarray = np.array(points)
        while rep < GameProperties.POINTS_CREATION_REPETITION_NUM.value:
            x: int = random.randint(0, Screen.WIDTH.value)
            y: int = random.randint(0, Screen.HEIGHT.value)
            if points.shape[0] == 0:
                return x, y
            x_dist: int = np.abs(points[:, 0] - x)
            y_dist: int = np.abs(points[:, 1] - y)
            result: List[bool] = (x_dist > PlayerProperties.WIDTH.value * 1.5) | (
                    y_dist > PlayerProperties.HEIGHT.value * 1.5)
            if all(result):
                return x, y
            rep += 1
        raise GenerationError('Generation of non-overlapping elements failed. \n'
                              'Try again by decreasing the number of elements (players, bombs, coins) \n'
                              'or increasing the number of generation attempts or change the map parameters.')


@lru_cache(maxsize=256)
def get_image(image_path: str, width: float, height: float) -> Optional[pygame.Surface]:
    cwd: str = os.path.dirname(os.path.dirname(__file__))
    image: pygame.Surface = pygame.image.load(os.path.join(cwd, image_path))
    image = pygame.transform.scale(image, (width + 2, height + 2))
    surface: pygame.Surface = pygame.Surface(image.get_size(), flags=pygame.SRCALPHA)
    surface.blit(image, (0, 0))
    return surface
