import pygame

from game.config import Screen, PlayerProperties, GameProperties, MOVE_DICT_REVERSE, Move
from game.board_elements.player import Player
from game.board_elements.bomb import Bomb
from game.board_elements.coin import Coin
from utils import RandomPosition
from typing import Tuple


class BomberManGameAttribute:
    def __init__(self):
        self.human_render: bool = False
        self.players_list: pygame.sprite.Group = pygame.sprite.Group()
        self.bombs_list: pygame.sprite.Group = pygame.sprite.Group()
        self.coins_list: pygame.sprite.Group = pygame.sprite.Group()

        self._set_players()
        self._set_bombs()
        self._set_coins()

    def _set_players(self) -> None:
        player_idx: int
        for player_idx in range(GameProperties.NUM_PLAYERS.value):
            color: Tuple
            if player_idx == GameProperties.HUMAN_IDX.value and GameProperties.HUMAN_PLAYER.value:
                color = PlayerProperties.HUMAN_PLAYER_COLOR.value
            else:
                color = PlayerProperties.BOT_PLAYER_COLOR.value
            player: Player = Player(*RandomPosition.get_x_y(), color=color)
            self.players_list.add(player)

    def _set_bombs(self):
        for _ in range(GameProperties.NUM_BOMBS.value):
            bomb: Bomb = Bomb(*RandomPosition.get_x_y())
            self.bombs_list.add(bomb)

    def _set_coins(self):
        for _ in range(GameProperties.NUM_COINS.value):
            coin: Coin = Coin(*RandomPosition.get_x_y())
            self.bombs_list.add(coin)


class BomberManGame:
    def __init__(self):
        self.attributes = BomberManGameAttribute()

        pygame.init()
        self.window = pygame.Surface((Screen.WIDTH.value, Screen.HEIGHT.value))
        pygame.display.set_caption("Bomber Man")

    def players(self):
        return self.attributes.players_list

    def update_players(self, actions: int):
        self.attributes.players_list.update(actions)

    def render(self, mode: str = 'human') -> None:
        if mode == 'human' and not self.attributes.human_render:
            self._turn_on_human_render()
            self.attributes.human_render = True

        if mode == 'human' and self.attributes.human_render:
            self._draw_elements()

    def _draw_elements(self) -> None:
        self.attributes.players_list.draw(self.window)
        self.attributes.bombs_list.draw(self.window)
        self.attributes.coins_list.draw(self.window)
        pygame.display.flip()

    def _turn_on_human_render(self) -> None:
        self.window = pygame.display.set_mode([Screen.WIDTH.value, Screen.HEIGHT.value])
        self.window.fill(Screen.BACKGROUND_COLOR.value)
        pygame.display.flip()

    def close(self) -> None:
        self.window = pygame.Surface((Screen.WIDTH.value, Screen.HEIGHT.value))
        pygame.event.pump()
        pygame.display.quit()

    def reset(self) -> None:
        self.attributes = BomberManGameAttribute()


if __name__ == '__main__':
    bm = BomberManGame()
    #bm.render('human')

    bm.reset()
    done = False
    clock = pygame.time.Clock()

    cur_agent = 0
    frame_count = 0
    quit_game = 0

    while not done:
        clock.tick(GameProperties.FPS.value)
        agents = bm.players()
        frame_count += 1
        actions = [-1 for x in range(len(agents))]
        cur_agent = GameProperties.HUMAN_IDX.value

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game = 1
                    break
                if event.key == pygame.K_BACKSPACE:
                    bm.reset()
                if event.key == pygame.K_c:
                    cur_agent += 1
                    if cur_agent > len(agents) - 1:
                        cur_agent = 0
                if event.key == pygame.K_w:
                    actions[cur_agent] = MOVE_DICT_REVERSE[Move.UP]
                if event.key == pygame.K_s:
                    actions[cur_agent] = MOVE_DICT_REVERSE[Move.DOWN]
                if event.key == pygame.K_a:
                    actions[cur_agent] = MOVE_DICT_REVERSE[Move.LEFT]
                if event.key == pygame.K_d:
                    actions[cur_agent] = MOVE_DICT_REVERSE[Move.RIGHT]

        if quit_game:
            break
        for a in actions:
            bm.update_players(a)
        bm.render()
        #done = any(env.dones.values())

    bm.close()
