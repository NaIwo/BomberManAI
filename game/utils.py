import random
from typing import Tuple

from config import Screen


class RandomPosition:
    @staticmethod
    def get_x_y() -> Tuple:
        x: int = random.randint(0, Screen.WIDTH.value)
        y: int = random.randint(0, Screen.HEIGHT.value)
        return x, y
