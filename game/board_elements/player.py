from typing import List, Tuple

from game.config import PlayerProperties, Move, NUMBER_TO_MOVE, Score
from .base_element import BaseElement


class Player(BaseElement):
    NAMESPACE: str = 'Player_{}'

    def __init__(self, left: int, top: int, idx: int):
        self.score: int = 0
        self.freezing_time: int = 0
        coordinates_tuple: Tuple = (left, top, PlayerProperties.WIDTH.value, PlayerProperties.HEIGHT.value)
        shape_properties: List = [PlayerProperties.WIDTH.value, PlayerProperties.HEIGHT.value]
        image_path: str = PlayerProperties.BOT_PLAYER_IMAGE_PATH.value
        color: Tuple = PlayerProperties.BOT_PLAYER_COLOR.value
        super().__init__(coordinates_tuple, Player.NAMESPACE.format(idx), shape_properties, color, image_path=image_path)

    def increase_player_score(self) -> None:
        if self.freezing_time == 0:
            self.score += Score.PICKED_COIN.value

    def decrease_score_and_freeze(self, freezing_time: int) -> None:
        if self.freezing_time == 0:
            self.score += Score.HIT_BY_BOMB.value
        self.freezing_time = freezing_time

    def update_move(self, move: int = -1) -> None:
        self.current_move = Move.NOT_MOVING if self.freezing_time > 0 else NUMBER_TO_MOVE[move]

    def update(self) -> None:
        if self.freezing_time > 0:
            self.freezing_time -= 1
            return
        move_tuple: Tuple = self.current_move.value
        self.rect.x += move_tuple[0] * Move.SPEED.value
        self.rect.y += move_tuple[1] * Move.SPEED.value
        self.clamp_position()

    def set_as_human_player(self):
        self._update_image(image_path=PlayerProperties.HUMAN_PLAYER_IMAGE_PATH.value)
        self._update_color(PlayerProperties.HUMAN_PLAYER_COLOR.value)
