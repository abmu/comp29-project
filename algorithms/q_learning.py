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
# REMINDER
# FIX POISSION RANDOM TRIP GENERATION!!!
#


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
        return random.choice(ACTION_SPACE)
    else:
        # exploitation - choose action with highest Q-value
        qs = [get_q(state, a) for a in ACTION_SPACE]
        return ACTION_SPACE[np.argmax(qs)]


def update_q(state: tuple[int, ...], action: int, reward: float, next_state: tuple[int, ...]) -> None:
    # update Q-value of state and action combinatoin based on reward and next state
    old_q = get_q(state, action)
    best_next = max([get_q(next_state, a) for a in ACTION_SPACE])
    Q[(state, action)] = old_q + ALPHA * (reward + GAMMA * best_next - old_q)


total_reward = 0

traci.start(SUMO_CONFIG)

for step in range(TOTAL_STEPS):
    state = get_state(tls_id, detector_ids, crossing_ids)
    action = choose_action(state)
    
    ....duration = perform_action(tls_id, action)

    traci.simulationStep()
    
    next_state = get_state(tls_id, detector_ids, crossing_ids)
    reward = get_reward(get_all_waiting_vehicles(detector_ids), get_all_waiting_peds(crossing_ids))
    update_q(state, action, reward, next_state)

    total_reward += reward

    print(f'Step: {step}, State: {state}, Reward: {reward}')

print(f'Total Reward: {total_reward}')

traci.close()