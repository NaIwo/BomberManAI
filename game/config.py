from enum import Enum
from typing import Dict


class GameProperties(Enum):
    NUM_PLAYERS = 2
    HUMAN_PLAYER = True
    HUMAN_IDX = 0
    NUM_BOMBS = 3
    NUM_COINS = 1
    FPS = 30


class Screen(Enum):
    WIDTH = 512
    HEIGHT = 512
    BACKGROUND_COLOR = (102, 153, 255)


class Move(Enum):
    NOT_MOVING = (0, 0)
    NUMBER_OF_MOVES = 4  # d not count 'not moving' state
    UP = (0, -1)
    DOWN = (0, 1)
    RIGHT = (1, 0)
    LEFT = (-1, 0)
    SPEED = 6


MOVE_DICT: Dict = {
    -1: Move.NOT_MOVING,
    0: Move.LEFT,
    1: Move.UP,
    2: Move.RIGHT,
    3: Move.DOWN
}

MOVE_DICT_REVERSE: Dict = {
    Move.NOT_MOVING: -1,
    Move.LEFT: 0,
    Move.UP: 1,
    Move.RIGHT: 2,
    Move.DOWN: 3
}


class Score(Enum):
    SCORE_LIMIT = 5
    PICKED_COIN = 1
    HIT_BY_BOMB = -1


class PlayerProperties(Enum):
    WIDTH = 20
    HEIGHT = 20
    BOT_PLAYER_COLOR = (204, 0, 0)
    HUMAN_PLAYER_COLOR = (0, 153, 51)


class BombProperties(Enum):
    WIDTH = PlayerProperties.WIDTH.value
    HEIGHT = PlayerProperties.HEIGHT.value
    EXPLOSION_WIDTH = PlayerProperties.WIDTH.value * 2
    EXPLOSION_HEIGHT = PlayerProperties.HEIGHT.value * 2
    COLOR = (0, 0, 0)
    EXPLOSION_COLOR = (255, 153, 0)
    TIME_TO_EXPLOSION = 50
    EXPLOSION_TIME = 50
    SLOWING_FACTOR = - Move.SPEED.value * 0.02


class CoinProperties(Enum):
    WIDTH = PlayerProperties.WIDTH.value
    HEIGHT = PlayerProperties.HEIGHT.value
    COLOR = (255, 255, 0)
