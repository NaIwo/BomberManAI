from enum import Enum
from typing import Dict
import os

base_image_path: str = os.path.join('game', 'board_elements', 'images')


class GameProperties(Enum):
    NUM_PLAYERS = 2
    NUM_BOMBS = 12
    NUM_COINS = 3
    FPS = 30
    POINTS_CREATION_REPETITION_NUM = 50
    LOAD_IMAGES = True
    TEXT_SIZE = 13
    TEXT_COLOR = (0, 0, 0)
    ITERATION_LIMIT = None


class Screen(Enum):
    WIDTH = 512
    HEIGHT = 512
    BACKGROUND_COLOR = (179, 179, 179)


class Move(Enum):
    NOT_MOVING = (0, 0)
    NUMBER_OF_MOVES = 4  # do not count 'not moving' state
    UP = (0, -1)
    DOWN = (0, 1)
    RIGHT = (1, 0)
    LEFT = (-1, 0)
    SPEED = 6


class Score(Enum):
    SCORE_LIMIT = 5
    PICKED_COIN = 1
    HIT_BY_BOMB = -1
    NOT_MOVING_PENALTY = -0.001


class PlayerProperties(Enum):
    BOT_PLAYER_IMAGE_PATH = os.path.join(base_image_path, 'player.png')
    HUMAN_PLAYER_IMAGE_PATH = os.path.join(base_image_path, 'human_player.png')
    WIDTH = 25
    HEIGHT = 25
    BOT_PLAYER_COLOR = (204, 0, 0)
    HUMAN_PLAYER_COLOR = (0, 153, 51)


class BombProperties(Enum):
    IMAGE_PATH = os.path.join(base_image_path, 'bomb.png')
    IMAGE_PATH_EXPLOSION = os.path.join(base_image_path, 'explosion.png')
    WIDTH = PlayerProperties.WIDTH.value
    HEIGHT = PlayerProperties.HEIGHT.value
    EXPLOSION_WIDTH = PlayerProperties.WIDTH.value * 3
    EXPLOSION_HEIGHT = PlayerProperties.HEIGHT.value * 3
    COLOR = (0, 0, 0)
    EXPLOSION_COLOR = (255, 153, 0)
    TIME_TO_EXPLOSION = 50
    EXPLOSION_TIME = 50
    SLOWING_FACTOR = - Move.SPEED.value * 0.02
    SPEED_MULTIPLICATION_FACTOR = 1.5
    TIME_TO_NEXT_TOUCH = 6


class CoinProperties(Enum):
    IMAGE_PATH = os.path.join(base_image_path, 'coin.png')
    WIDTH = PlayerProperties.WIDTH.value
    HEIGHT = PlayerProperties.HEIGHT.value
    COLOR = (255, 255, 0)


NUMBER_TO_MOVE: Dict = {
    0: Move.LEFT,
    1: Move.UP,
    2: Move.RIGHT,
    3: Move.DOWN,
    4: Move.NOT_MOVING,
}

MOVE_TO_NUMBER: Dict = {
    Move.LEFT: 0,
    Move.UP: 1,
    Move.RIGHT: 2,
    Move.DOWN: 3,
    Move.NOT_MOVING: 4
}