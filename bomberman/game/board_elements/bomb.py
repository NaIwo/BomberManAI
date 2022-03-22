from typing import Tuple, List

from bomberman.game.config import BombProperties, Move, Screen, NUMBER_TO_MOVE, MOVE_TO_NUMBER
from .base_element import BaseElement


class Bomb(BaseElement):
    NAMESPACE: str = 'Bomb_{}'

    def __init__(self, left: int, top: int, idx: int):
        # if bomb during explosion, time_to_explosion is getting negative
        self.time_to_explosion: int = BombProperties.TIME_TO_EXPLOSION.value
        self.speed: int = 0
        # if bomb has ever been touched
        self.touched: bool = False
        self.exploded: bool = False
        self.time_to_next_touch: int = 0
        coordinates_tuple: Tuple = (left, top, BombProperties.WIDTH.value, BombProperties.HEIGHT.value)
        shape_properties: List = [BombProperties.WIDTH.value, BombProperties.HEIGHT.value]
        super().__init__(coordinates_tuple, Bomb.NAMESPACE.format(idx), shape_properties,
                         color=BombProperties.COLOR.value, image_path=BombProperties.IMAGE_PATH.value)

    def update_move_information(self, move: int) -> None:
        if not self._can_be_touch():
            return
        self.time_to_next_touch = BombProperties.TIME_TO_NEXT_TOUCH.value
        self.touched = True
        if NUMBER_TO_MOVE[move] != Move.NOT_MOVING:
            self.current_move = NUMBER_TO_MOVE[move]
            self.speed = Move.SPEED.value * BombProperties.SPEED_MULTIPLICATION_FACTOR.value
        else:
            new_move: int = (MOVE_TO_NUMBER[self.current_move] + 2) % Move.NUMBER_OF_MOVES.value
            self.current_move = NUMBER_TO_MOVE[new_move]

    def update(self) -> None:
        self._kill_if_necessary()
        self._update_explosion_information()
        self._decrease_time_to_next_touch()
        self._set_speed()
        if self.speed == 0:
            return
        self._set_new_position()

    def _kill_if_necessary(self) -> None:
        if self.time_to_end_explosion() == 0:
            self.kill()

    def _decrease_time_to_next_touch(self) -> None:
        self.time_to_next_touch = max(self.time_to_next_touch - 1, 0)

    def _set_speed(self) -> None:
        self.speed = max(self.speed + BombProperties.SLOWING_FACTOR.value, 0)

    def _set_new_position(self) -> None:
        self.rect.x += self.current_move.value[0] * self.speed
        self.rect.y += self.current_move.value[1] * self.speed
        self.clamp_position()

    def _update_explosion_information(self) -> None:
        if not self.touched:
            return
        if self.time_to_explosion <= 0 and (not self.exploded):
            self._set_bomb_properties_as_exploded()
        # if bomb during explosion, time_to_explosion is getting negative
        self.time_to_explosion = max(self.time_to_explosion - 1, -BombProperties.EXPLOSION_TIME.value)

    def _set_bomb_properties_as_exploded(self) -> None:
        self.speed = 0
        self.exploded = True
        left: int = max(self.rect.centerx - (BombProperties.EXPLOSION_WIDTH.value // 2), 0)
        top: int = max(self.rect.centery - (BombProperties.EXPLOSION_HEIGHT.value // 2), 0)
        coordinates_tuple: Tuple = (
            left, top, BombProperties.EXPLOSION_WIDTH.value, BombProperties.EXPLOSION_HEIGHT.value)
        shape_properties: List = [BombProperties.EXPLOSION_WIDTH.value, BombProperties.EXPLOSION_HEIGHT.value]
        self._update_properties(coordinates_tuple, shape_properties, BombProperties.EXPLOSION_COLOR.value)
        self._update_image(BombProperties.IMAGE_PATH_EXPLOSION.value)

    def auto_explosion(self):
        if not self.is_during_explosion():
            self.touched = True
            self.time_to_explosion = 0
            self.speed = 0

    def clamp_position(self) -> None:
        max_x: int = Screen.WIDTH.value - BombProperties.WIDTH.value
        max_y: int = Screen.HEIGHT.value - BombProperties.HEIGHT.value
        new_x = max(min(max_x, self.rect.x), 0)
        new_y = max(min(max_y, self.rect.y), 0)
        if self.rect.x != new_x or self.rect.y != new_y:
            new_move: int = (MOVE_TO_NUMBER[self.current_move] + 2) % Move.NUMBER_OF_MOVES.value
            self.current_move = NUMBER_TO_MOVE[new_move]
        self.rect.x, self.rect.y = new_x, new_y

    def time_to_end_explosion(self) -> int:
        # if bomb during explosion, time_to_explosion is getting negative
        return BombProperties.EXPLOSION_TIME.value + self.time_to_explosion

    def is_during_explosion(self) -> bool:
        return (self.time_to_explosion >= -BombProperties.EXPLOSION_TIME.value) and (self.time_to_explosion <= 0)

    def was_touched(self) -> bool:
        return self.touched

    def _can_be_touch(self) -> bool:
        """
        protects against an infinite number of reflections
        """
        if self.time_to_next_touch == 0:
            return True
        else:
            return False
