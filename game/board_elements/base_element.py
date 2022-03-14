from pygame.sprite import Sprite

from game.config import PlayerProperties, Screen


class BaseElement(Sprite):
    def __init__(self):
        super().__init__()

    def update(self, move: int) -> None:
        pass

    def clamp_position(self) -> None:
        max_x: int = Screen.WIDTH.value - PlayerProperties.WIDTH.value
        max_y: int = Screen.HEIGHT.value - PlayerProperties.HEIGHT.value
        self.rect.x = max(min(max_x, self.rect.x), 0)
        self.rect.y = max(min(max_y, self.rect.y), 0)
