from model import Model
from bomberman import parallel_env
from custom_eaGenerateUpdate import eaGenerateUpdate

import numpy as np
import os
import datetime
from collections import defaultdict
from itertools import chain
from typing import Dict, DefaultDict, List, Optional
from deap import creator, base, cma, tools

NUM_PLAYERS: int = 4
LAMBDA: int = NUM_PLAYERS * 8
NGEN: int = 500

SAVE_PATH: str = os.path.join('.', 'CMA', datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), 'weights.npy')
os.makedirs(SAVE_PATH[:SAVE_PATH.rfind(os.sep)], exist_ok=False)


# np.random.seed(42)


def env_creator():
    return parallel_env(num_players=NUM_PLAYERS, num_bombs=3, num_coins=6, score_limit=10, iteration_limit=1000)


def evaluate(individuals) -> List:
    env = env_creator()
    observations = env.reset()

    policies: Dict = dict()

    agent: str
    weights: Optional[np.ndarray]
    for agent, weights in zip(env.agents, individuals):
        observation_space = env.observation_space(agent)
        act_space = env.action_space(agent)
        policies[agent] = Model.from_weights(observation_space, act_space.n, weights)

    rewards_sum: DefaultDict = defaultdict(int)
    done: bool = False
    while not done:
        actions: Dict = dict()
        for agent in env.agents:
            action_probabilities: np.ndarray = policies[agent](observations[agent])
            actions[agent] = np.argmax(action_probabilities)
        observations, rewards, dones, _ = env.step(actions)
        done = (sum(dones.values()) > 0)
        for agent, reward in rewards.items():
            rewards_sum[agent] += reward
    env.close()
    return [(rew,) for agent, rew in rewards_sum.items()]


def custom_map_func(evaluate_func, population):
    elements: np.ndarray = np.array(population).reshape(-1, NUM_PLAYERS, len(population[0]))
    #  np.random.shuffle(elements)
    return chain.from_iterable(map(evaluate_func, elements))


def train():
    env = env_creator()

    observation_space = env.observation_space(env.agents[0])
    act_space = env.action_space(env.agents[0])
    temp_model: Model = Model(observation_space, act_space.n)

    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    toolbox = base.Toolbox()
    strategy = cma.Strategy(centroid=list(np.random.uniform(-5.0, 5.0, temp_model.num_parameters)),
                            sigma=np.random.uniform(0.0, 5.0, 1)[0], lambda_=LAMBDA)
    toolbox.register("generate", strategy.generate, creator.Individual)
    toolbox.register("update", strategy.update)
    toolbox.register("evaluate", lambda ind: evaluate(ind))
    toolbox.register("map", custom_map_func)

    del temp_model

    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    eaGenerateUpdate(toolbox, ngen=NGEN, stats=stats, halloffame=hof, save_path=SAVE_PATH)


if __name__ == '__main__':
    train()
