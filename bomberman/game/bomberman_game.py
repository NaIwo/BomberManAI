import pygame
from pygame.sprite import Sprite, Group
from typing import List, Dict, Union, Optional
import numpy as np

from bomberman.game.config import Screen, GameProperties, Move, Score, MOVE_TO_NUMBER, Rewards
from bomberman.game.board_elements import Player, Bomb, Coin
from bomberman.game.utils import RandomValues


class BomberManGameAttribute:
    def __init__(self, num_players: int, num_bombs: int, num_coins: int, score_limit: int,
                 iteration_limit: Optional[int], human_player_idx: Optional[int]):
        self.num_players: int = num_players
        self.num_bombs: int = num_bombs
        self.num_coins: int = num_coins
        self.score_limit: int = score_limit
        self.winner_idx: List = list()
        self.iteration_limit: Optional[int] = iteration_limit
        self.human_player_idx: Optional[int] = human_player_idx

        self.number_of_performed_iterations: int = 0
        self.human_render: bool = False
        self.closed: bool = False
        self.end_game: bool = False
        self.players_list: Group = Group()
        self.bombs_list: Group = Group()
        self.coins_list: Group = Group()

        """
        Observation:
        [player x; player y; player move direction; player score] for each player
        [bomb x; bomb y; bomb move direction; is during explosion; speed] for each bomb
        [coin x; coin y] for each coin

        so dimensionality is: 5*number_of_bombs + 2*number_of_coins + 4*number_of_players
        
        but 'move direction' are categorical, so we change them into one-hot.
        
        finally:
        
        9*number_of_bombs + 2*number_of_coins + 8*number_of_players
        
        We will also add requesting player idx as one-hot, but only in 'get_observations' function'
        """
        self._observations: Dict = {
            'players': np.zeros(shape=(self.num_players, 8)),
            'bombs': np.zeros(shape=(self.num_bombs, 9)),
            'coins': np.zeros(shape=(self.num_coins, 2))
        }
        self._score_idx: int = -1

        self._add_players()
        self._update_bombs_attributes()
        self._update_coins_attributes()

        self.set_human_player_if_necessary()

    def _add_players(self) -> None:
        player_idx: int
        for player_idx in range(self.num_players):
            player: Player = Player(*RandomValues.get_x_y_without_overlapping(self.get_all_points()), idx=player_idx)
            self.players_list.add(player)
            local_observation: List = [player.rect.centerx, player.rect.centery, *player.get_current_move_as_one_hot(),
                                       player.score]
            self._observations['players'][player_idx] = np.array(local_observation)

    def set_human_player_if_necessary(self) -> None:
        if self.human_player_idx is not None:
            self.players_list.sprites()[self.human_player_idx].set_as_human_player()

    def update(self) -> None:
        if self.iteration_limit:
            self.number_of_performed_iterations += 1
            self.end_game = (self.number_of_performed_iterations >= self.iteration_limit) or self.end_game

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
            if player.score == self.score_limit:
                self.end_game = True
                self.winner_idx.append(player_idx)

    def _update_bombs_attributes(self):
        bomb_idx: int
        for bomb_idx in range(self.num_bombs):
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
        for coin_idx in range(self.num_coins):
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
        return np.concatenate((
            self._get_player_idx_as_one_hot(agent_idx),
            self._observations['players'].flatten(),
            self._observations['bombs'].flatten(),
            self._observations['coins'].flatten()
        ))

    def _get_player_idx_as_one_hot(self, agent_idx: int) -> np.ndarray:
        return np.eye(self.num_players)[agent_idx]

    def get_players_scores(self) -> np.ndarray:
        return self._observations['players'][:, self._score_idx]

    def get_number_of_features(self) -> int:
        """
        self.num_players - one-hot encoding of player idx
        """
        return self.num_players + (self.num_players * 8) + (self.num_bombs * 9) + (self.num_coins * 2)


class BomberManGame:
    def __init__(self, num_players: int = GameProperties.NUM_PLAYERS.value,
                 num_bombs: int = GameProperties.NUM_BOMBS.value,
                 num_coins: int = GameProperties.NUM_COINS.value,
                 score_limit: int = Score.SCORE_LIMIT.value,
                 iteration_limit: Optional[int] = GameProperties.ITERATION_LIMIT.value,
                 human_player_idx: Optional[int] = None):
        self.attributes = BomberManGameAttribute(num_players=num_players, num_bombs=num_bombs,
                                                 num_coins=num_coins, score_limit=score_limit,
                                                 iteration_limit=iteration_limit, human_player_idx=human_player_idx)

        pygame.init()
        pygame.font.init()
        self.window = pygame.Surface((Screen.WIDTH.value, Screen.HEIGHT.value))
        self.font = pygame.font.SysFont('Helvetica', GameProperties.TEXT_SIZE.value)
        pygame.display.set_caption("Bomber Man")

    @property
    def players(self):
        return self.attributes.players_list

    def players_names(self) -> List[str]:
        player: Sprite
        return [player.name for player in self.attributes.players_list]

    @property
    def score_limit(self) -> int:
        return self.attributes.score_limit

    def perform_action_and_get_reward(self, agent_idx: int, action: int) -> float:
        agent: Sprite = self.attributes.players_list.sprites()[agent_idx]
        score: int = agent.score
        agent.update_move(action)
        self._handle_bombs_events(agent, action)
        self._handle_coins_events(agent)
        diff: int = agent.score - score
        return self._get_reward(diff)

    @staticmethod
    def _get_reward(diff: int) -> float:
        reward: float = Rewards.EACH_ITERATION_PENALTY.value
        if diff > 0:
            reward += Rewards.PICKED_COIN.value
        elif diff < 0:
            reward += Rewards.HIT_BY_BOMB.value
        return reward

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
                agent.decrease_score_and_freeze(freezing_time=bomb.time_to_end_explosion() + 1)

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

    @staticmethod
    def get_number_of_possible_moves() -> int:
        return Move.NUMBER_OF_MOVES.value + 1

    def get_winners_idx(self) -> List[int]:
        return self.attributes.winner_idx

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
            text = self.font.render(f'player_{player_idx}:  {int(score)}  /  {self.attributes.score_limit}', False,
                                    GameProperties.TEXT_COLOR.value)
            self.window.blit(text, (0, GameProperties.TEXT_SIZE.value * player_idx))

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
        self.attributes = BomberManGameAttribute(num_players=self.attributes.num_players,
                                                 num_bombs=self.attributes.num_bombs,
                                                 num_coins=self.attributes.num_coins,
                                                 score_limit=self.attributes.score_limit,
                                                 iteration_limit=self.attributes.iteration_limit,
                                                 human_player_idx=self.attributes.human_player_idx)
