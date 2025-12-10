import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

import numpy as np
import random
from environment import SUMO_CONFIG, TOTAL_STEPS, tls_id, queue_ids, crossing_ids, ACTION_SPACE, get_state, perform_action, set_route
from utils import file_dump, file_eval


TRAIN_MODE = False

RESULTS_FILE = 'results/q_learning.txt'
Q_TABLE_FILE = 'results/q_table.txt'

Q = {} # {(state, action): value}

SEED = 29

# Q-learning hyperparameters
ALPHA = 0.1 # learning rate
GAMMA = 0.9 # discount factor
EPSILON = 1.0 # exploration rate
EPSILON_DECAY = 0.995
EPSILON_MIN = 0.005

EPISODES = 1000

if not TRAIN_MODE:
    Q = file_eval(Q_TABLE_FILE)[0]
    EPSILON = 0
    EPSILON_MIN = 0


def get_q(state: tuple[int, ...], action: int) -> float:
    # return Q-value of state and action combination
    return Q.get((state, action), 0.0)


def choose_action(state: tuple[int, ...]) -> int:
    # choose action using an epsilon-greedy policy
    actions = list(ACTION_SPACE.keys())
    if random.random() < EPSILON:
        # exploration - choose random action
        return random.choice(actions)
    else:
        # exploitation - choose action with highest Q-value
        qs = [get_q(state, a) for a in actions]
        return actions[np.argmax(qs)]


def update_q(state: tuple[int, ...], action: int, reward: float, next_state: tuple[int, ...], duration: float) -> None:
    # update Q-value of state and action combinatoin based on reward and next state
    actions = list(ACTION_SPACE.keys())
    old_q = get_q(state, action)
    best_next = max(get_q(next_state, a) for a in actions)
    # Semi-Markov Decision Process
    Q[(state, action)] = old_q + ALPHA * (reward + (GAMMA ** duration) * best_next - old_q)


def run() -> tuple[float, float]:
    # run a single episode and return the reward
    global EPSILON

    total_reward = 0
    step = 0
    
    traci.start(SUMO_CONFIG)

    while step < TOTAL_STEPS:
        state = get_state(tls_id, queue_ids, crossing_ids)
        action = choose_action(state)
        
        step, reward, duration = perform_action(tls_id, step, TOTAL_STEPS, action)

        next_state = get_state(tls_id, queue_ids, crossing_ids)
        total_reward += reward

        if TRAIN_MODE:
            update_q(state, action, reward, next_state, duration)

        # print(f'Step: {step}, State: {state}, Action: {action}, Reward: {reward}')

    traci.close()

    EPSILON = max(EPSILON_MIN, EPSILON * EPSILON_DECAY)

    if TRAIN_MODE:
        file_dump(Q_TABLE_FILE, str(Q))

    return total_reward


if __name__ == "__main__":
    episode_rewards = []

    random.seed(SEED)

    for episode in range(1, EPISODES+1):

        print(f'Episode: {episode}')
        
        # set SUMO route
        set_route(episode)

        # run episode training
        print(f'Running SUMO...')
        reward = run()
        episode_rewards.append(reward)

        print(f'Total Reward: {reward}, Epsilon: {EPSILON}\n')
        if TRAIN_MODE:
            file_dump(RESULTS_FILE, str(episode_rewards))