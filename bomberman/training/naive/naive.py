import numpy as np
from typing import Dict, List
from scipy.spatial.distance import cdist

from bomberman.game.config import BombProperties, Screen, Move, MOVE_TO_NUMBER

"""
This algorithm is hardcoded with respect to observations constructed in 'bomberman_game.py'.
If this observations was changed, below code should be also changed.
"""


def naive(observations: np.ndarray, properties: Dict) -> int:
    bomb_shape: np.ndarray = np.array([BombProperties.WIDTH.value / Screen.WIDTH.value,
                                       BombProperties.HEIGHT.value / Screen.HEIGHT.value])
    agent_xy: np.ndarray = observations[:2]
    observations = observations[2:]
    coins: np.ndarray = get_x_y(observations[:properties['num_coins'] * 2], agent_xy, 2)
    observations = observations[properties['num_coins'] * 2:]
    players: np.ndarray = get_x_y(observations[:(properties['num_players'] - 1) * 3], agent_xy, 3)
    observations = observations[(properties['num_players'] - 1) * 3:]
    bombs: np.ndarray = get_x_y(observations, agent_xy, 3)

    agent_xy = np.expand_dims(agent_xy, axis=0)
    coins_distances: np.ndarray = cdist(agent_xy, coins, metric='cityblock')[0]
    sorted_coins: np.ndarray = np.argsort(coins_distances)
    other_players_distances: np.ndarray = cdist(players[:, :2], coins, metric='cityblock')

    flag: bool = False
    for idx in range(properties['num_coins']):
        selected_coin: int = sorted_coins[idx]
        if not (other_players_distances[:, selected_coin] < coins_distances[selected_coin]).any():
            flag = True
            break
    if not flag:
        selected_coin = sorted_coins[0]
    selected_target: np.ndarray = coins[selected_coin, :]
    dist: np.ndarray = (agent_xy - selected_target)[0]
    greater_dist_dim: int = int(np.argmax(np.abs(dist)))
    sign: float = np.sign(dist[greater_dist_dim])

    action: int
    if greater_dist_dim == 0:
        if sign == 1.0:
            action = MOVE_TO_NUMBER[Move.LEFT]
        else:
            action = MOVE_TO_NUMBER[Move.RIGHT]
    else:
        if sign == 1.0:
            action = MOVE_TO_NUMBER[Move.UP]
        else:
            action = MOVE_TO_NUMBER[Move.DOWN]

    bombs_during_explosion: np.ndarray = bombs[np.where(bombs[:, 2] == 1)]
    if bombs_during_explosion.any():
        if (cdist(agent_xy, bombs_during_explosion[:, :2], metric='cityblock') < max(bomb_shape) * 1.5).any():
            action = MOVE_TO_NUMBER[Move.NOT_MOVING]

    return action


def get_x_y(observations: np.ndarray, agent_xy: np.ndarray, attributes_per_element: int) -> np.ndarray:
    results: List = list()
    for obs in observations.reshape(-1, attributes_per_element):
        results.append(agent_xy - obs) if attributes_per_element == 2 else results.append(
            np.concatenate([agent_xy - obs[:2], [obs[2]]]))

    return np.array(results)
