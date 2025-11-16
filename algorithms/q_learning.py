import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

import numpy as np
import random
from settings import SUMO_CONFIG, TOTAL_STEPS, tls_id, detector_ids, crossing_ids
from state import get_state, get_all_waiting_vehicles, get_all_waiting_peds
from action import ACTION_SPACE, perform_action
from reward import get_reward


# TODO
#
# Generate new routes dynamically after each episode to ensure new training data and prevent overfitting
#
# Automate training process by removing GUI
#
# Create separate python package for the state, action, reward files


RANDOM_SEED = 42
random.seed(RANDOM_SEED)

Q = {} # {(state, action): value}

# Q-learning hyperparameters
ALPHA = 0.1 # learning rate
GAMMA = 0.9 # discount factor
EPSILON = 0.2 # exploration rate
EPISODES = 100


def get_q(state: tuple[int, ...], action: int) -> float:
    # return Q-value of state and action combination
    return Q.get((state, action), 0.0)


def choose_action(state: tuple[int, ...]) -> int:
    # choose action using an epsilon-greedy policy
    if random.random() < EPSILON:
        # exploration - choose random action
        return random.choice(list(ACTION_SPACE.keys()))
    else:
        # exploitation - choose action with highest Q-value
        qs = [get_q(state, a) for a in ACTION_SPACE]
        return list(ACTION_SPACE.keys())[np.argmax(qs)]


def update_q(state: tuple[int, ...], action: int, reward: float, next_state: tuple[int, ...]) -> None:
    # update Q-value of state and action combinatoin based on reward and next state
    old_q = get_q(state, action)
    best_next = max([get_q(next_state, a) for a in ACTION_SPACE])
    Q[(state, action)] = old_q + ALPHA * (reward + GAMMA * best_next - old_q)


for episode in range(EPISODES):
    traci.start(SUMO_CONFIG)

    total_reward = 0

    prev_action = None

    step = 0
    while step < TOTAL_STEPS:
        state = get_state(tls_id, detector_ids, crossing_ids)
        curr_action = choose_action(state)
        
        step = perform_action(tls_id, step, TOTAL_STEPS, curr_action, prev_action)

        prev_action = curr_action

        next_state = get_state(tls_id, detector_ids, crossing_ids)
        reward = get_reward(get_all_waiting_vehicles(detector_ids), get_all_waiting_peds(crossing_ids))
        update_q(state, curr_action, reward, next_state)
        total_reward += reward

        print(f'Step: {step}, State: {state}, Reward: {reward}')

    print(f'Total Reward: {total_reward}')
    print(f'Q-Table: {Q}')

    traci.close()