import pygame
from pygame.sprite import Sprite, Group

from game.config import Screen, GameProperties, MOVE_TO_NUMBER, Move, Score
from game.board_elements import Player, Bomb, Coin
from utils import RandomValues
from typing import List, Dict, Union, Optional
import numpy as np


class BomberManGameAttribute:
    def __init__(self):
        self.human_render: bool = False
        self.closed: bool = False
        self.end_game: bool = False
        self.players_list: Group = Group()
        self.bombs_list: Group = Group()
        self.coins_list: Group = Group()

        """
        Observation:
        [player x; player y; player move direction; player score] for each player - 
                                                    current agent requesting observations will be listed first
        [bomb x; bomb y; bomb move direction; is during explosion; speed] for each bomb
        [coin x; coin y] for each coin

        so dimensionality is: 5*number_of_bombs + 2*number_of_coins + 4*number_of_players
        
        but 'move direction' are categorical, so we change them into one-hot.
        
        finally:
        
        9*number_of_bombs + 2*number_of_coins + 8*number_of_players
        """
        self._observations: Dict = {
            'players': np.zeros(shape=(GameProperties.NUM_PLAYERS.value, 8)),
            'bombs': np.zeros(shape=(GameProperties.NUM_BOMBS.value, 9)),
            'coins': np.zeros(shape=(GameProperties.NUM_COINS.value, 2))
        }
        self._score_idx: int = 7

        self._add_players()
        self._update_bombs_attributes()
        self._update_coins_attributes()

    def _add_players(self) -> None:
        player_idx: int
        for player_idx in range(GameProperties.NUM_PLAYERS.value):
            color_source: str
            if player_idx == GameProperties.HUMAN_IDX.value and GameProperties.HUMAN_PLAYER.value:
                color_source = 'HUMAN'
            else:
                color_source = 'BOT'
            player: Player = Player(*RandomValues.get_x_y_without_overlapping(self.get_all_points()),
                                    color_source=color_source, idx=player_idx)
            self.players_list.add(player)
            local_observation: List = [player.rect.centerx, player.rect.centery, *player.get_current_move_as_one_hot(),
                                       player.score]
            self._observations['players'][player_idx] = np.array(local_observation)

    def update(self) -> None:
        self._update_players_observations()
        self._update_bombs_attributes()
        self._update_coins_attributes()

    def _update_players_observations(self) -> None:
        player_idx: int
        player: Sprite
        for player_idx, player in enumerate(self.players_list):
            local_observation: List = [player.rect.centerx, player.rect.centery, *player.get_current_move_as_one_hot(),
                                       player.score]
            self._observations['players'][player_idx] = np.array(local_observation)
            self.end_game = (player.score == Score.SCORE_LIMIT.value) or self.end_game

    def _update_bombs_attributes(self):
        bomb_idx: int
        for bomb_idx in range(GameProperties.NUM_BOMBS.value):
            bomb: Union[Bomb, Sprite]
            if not self.bombs_list.has(bomb_idx):
                bomb = Bomb(*RandomValues.get_x_y_without_overlapping(self.get_all_points()), idx=bomb_idx)
                self.bombs_list.add(bomb)
            else:
                bomb = self.bombs_list.sprites()[bomb_idx]
            local_observation: List = [bomb.rect.centerx, bomb.rect.centery, *bomb.get_current_move_as_one_hot(),
                                       bomb.is_during_explosion(), bomb.speed]
            self._observations['bombs'][bomb_idx] = np.array(local_observation)

    def _update_coins_attributes(self):
        coin_idx: int
        for coin_idx in range(GameProperties.NUM_COINS.value):
            coin: Union[Coin, Sprite]
            if not self.coins_list.has(coin_idx):
                coin = Coin(*RandomValues.get_x_y_without_overlapping(self.get_all_points()), idx=coin_idx)
                self.coins_list.add(coin)
            else:
                coin = self.coins_list.sprites()[coin_idx]
            local_observation: List = [coin.rect.centerx, coin.rect.centery]
            self._observations['coins'][coin_idx] = np.array(local_observation)

    def get_all_points(self) -> List[List]:
        points = list()
        elements_group: Group
        for elements_group in [self.players_list, self.bombs_list, self.coins_list]:
            element: Sprite
            for element in elements_group:
                point: List = [element.rect.centerx, element.rect.centery]
                points.append(point)
        return points

    def get_observations(self, agent_idx: int) -> np.ndarray:
        """
        First we place an agent requesting for observation
        """
        current_agent_obs: np.ndarray = self._observations['players'][agent_idx]
        rest_agents_obs: np.ndarray = np.delete(self._observations['players'], agent_idx, axis=0)
        return np.concatenate((
            np.concatenate((current_agent_obs.flatten(),
                            rest_agents_obs.flatten())),
            self._observations['bombs'].flatten(),
            self._observations['coins'].flatten()
        ))

    def get_players_scores(self) -> np.ndarray:
        return self._observations['players'][:, self._score_idx]

    @staticmethod
    def get_number_of_features() -> int:
        return (GameProperties.NUM_PLAYERS.value * 8) + (GameProperties.NUM_BOMBS.value * 9) + (
                GameProperties.NUM_COINS.value * 2)


class BomberManGame:
    def __init__(self):
        self.attributes = BomberManGameAttribute()

        pygame.init()
        pygame.font.init()
        self.window = pygame.Surface((Screen.WIDTH.value, Screen.HEIGHT.value))
        self.font = pygame.font.SysFont('Helvetica', GameProperties.TEXT_SIZE.value)
        pygame.display.set_caption("Bomber Man")

    @property
    def players(self):
        return self.attributes.players_list

    def update_board_info_by_player_action(self, agent_idx: int, action: int):
        agent: Sprite = self.attributes.players_list.sprites()[agent_idx]
        agent.update_move(action)
        self._handle_bombs_events(agent, action)
        self._handle_coins_events(agent)

    def _handle_bombs_events(self, agent: Sprite, action: int):
        self._agent_interaction(agent, action)
        self._bombs_interactions()

    def _agent_interaction(self, agent: Sprite, action: int) -> None:
        player_bombs: List = pygame.sprite.spritecollide(agent, self.attributes.bombs_list, False)
        bomb: Sprite
        for bomb in player_bombs:
            if bomb.time_to_explosion > 0:
                bomb.update_move_information(action)
            elif bomb.is_during_explosion():
                agent.decrease_score_and_freeze(freezing_time=bomb.time_to_end_explosion())

    def _bombs_interactions(self) -> None:
        bombs_and_bombs: Dict = pygame.sprite.groupcollide(self.attributes.bombs_list, self.attributes.bombs_list,
                                                           False, False)
        bomb_source: Sprite
        bomb_target_list: List
        for bomb_source, bomb_target_list in bombs_and_bombs.items():
            bomb_target: Sprite
            for bomb_target in bomb_target_list:
                if bomb_source == bomb_target:
                    continue
                if bomb_source.is_during_explosion() and (not bomb_target.is_during_explosion()):
                    bomb_target.auto_explosion()
                elif bomb_source.was_touched() and (not bomb_source.is_during_explosion()):
                    bomb_source.update_move_information(MOVE_TO_NUMBER[Move.NOT_MOVING])

    def _handle_coins_events(self, agent: Sprite):
        self._collect_coins(agent)
        self._explode_coins()

    def _collect_coins(self, agent: Sprite) -> None:
        collision_coins: List = pygame.sprite.spritecollide(agent, self.attributes.coins_list, False)
        coin: Sprite
        for coin in collision_coins:
            agent.increase_player_score()
            coin.collected_by_player = True

    def _explode_coins(self) -> None:
        exploded_coins: Dict = pygame.sprite.groupcollide(self.attributes.coins_list, self.attributes.bombs_list,
                                                          False, False)
        coin: Sprite
        bombs: Dict
        for coin, bombs in exploded_coins.items():
            bomb: Sprite
            if any([bomb.is_during_explosion() for bomb in bombs]):
                coin.destroyed_by_bomb = True

    def update(self):
        self.attributes.players_list.update()
        self.attributes.coins_list.update()
        self.attributes.bombs_list.update()

        self.attributes.update()

    def get_observations(self, agent_idx: int) -> np.ndarray:
        return self.attributes.get_observations(agent_idx)

    def get_number_of_features(self) -> int:
        return self.attributes.get_number_of_features()

    def is_end_game(self) -> bool:
        return self.attributes.end_game

    def render(self, mode: str = 'human') -> Optional[np.ndarray]:
        if mode == 'human' and not self.attributes.human_render:
            self._turn_on_human_render()
            self.attributes.human_render = True

        if mode == 'human' and self.attributes.human_render:
            self._draw_elements()

        if mode == 'rgb_array':
            board: np.ndarray = np.array(pygame.surfarray.pixels3d(self.window))
            return np.transpose(board, axes=(1, 0, 2))

    def _draw_elements(self) -> None:
        self.window.fill(Screen.BACKGROUND_COLOR.value)
        self.attributes.players_list.draw(self.window)
        self.attributes.bombs_list.draw(self.window)
        self.attributes.coins_list.draw(self.window)
        self.render_text()
        pygame.display.flip()

    def render_text(self) -> None:
        scores: np.ndarray = self.attributes.get_players_scores()
        for player_idx, score in enumerate(scores):
            text = self.font.render(f'player_{player_idx}:  {int(score)}  /  {Score.SCORE_LIMIT.value}', False, GameProperties.TEXT_COLOR.value)
            self.window.blit(text, (0, GameProperties.TEXT_SIZE.value*player_idx))

    def _turn_on_human_render(self) -> None:
        self.window = pygame.display.set_mode([Screen.WIDTH.value, Screen.HEIGHT.value])
        self.window.fill(Screen.BACKGROUND_COLOR.value)
        pygame.display.flip()

    def close(self) -> None:
        if self.attributes.human_render and (not self.attributes.closed):
            self.attributes.human_render = False
            pygame.event.pump()
            pygame.display.quit()
        if not self.attributes.closed:
            self.attributes.closed = True

    def reset(self) -> None:
        self.attributes = BomberManGameAttribute()


if __name__ == '__main__':
    bm = BomberManGame()
    # bm.render('human')

    bm.reset()
    done = False
    clock = pygame.time.Clock()
    cur_agent = 0
    quit_game = 0
    cur_agent = GameProperties.HUMAN_IDX.value

    while not done:
        clock.tick(GameProperties.FPS.value)
        actions = [-1 for x in range(len(bm.players))]

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game = 1
                    break
                if event.key == pygame.K_BACKSPACE:
                    bm.reset()
                if event.key == pygame.K_c:
                    cur_agent += 1
                    if cur_agent == len(bm.players):
                        cur_agent = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            actions[cur_agent] = MOVE_TO_NUMBER[Move.UP]
        if keys[pygame.K_s]:
            actions[cur_agent] = MOVE_TO_NUMBER[Move.DOWN]
        if keys[pygame.K_a]:
            actions[cur_agent] = MOVE_TO_NUMBER[Move.LEFT]
        if keys[pygame.K_d]:
            actions[cur_agent] = MOVE_TO_NUMBER[Move.RIGHT]

        if quit_game:
            break
        for agent_idx, action in enumerate(actions):
            bm.update_board_info_by_player_action(agent_idx, action)
        bm.update()
        bm.render()
        # done = any(env.dones.values())

    bm.close()
