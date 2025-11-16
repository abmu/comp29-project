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
# Generate new routes dynamically after each episode to ensure new training data and prevent overfitting, random weighted edges, random density


RANDOM_SEED = 42
random.seed(RANDOM_SEED)

Q = {} # {(state, action): value}

# Q-learning hyperparameters
ALPHA = 0.1 # learning rate
GAMMA = 0.9 # discount factor
EPSILON = 1.0 # exploration rate
EPSILON_DECAY = 0.995
EPSILON_MIN = 0.005
EPISODES = 100


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


def update_q(state: tuple[int, ...], action: int, reward: float, next_state: tuple[int, ...]) -> None:
    # update Q-value of state and action combinatoin based on reward and next state
    actions = list(ACTION_SPACE.keys())
    old_q = get_q(state, action)
    best_next = max(get_q(next_state, a) for a in actions)
    Q[(state, action)] = old_q + ALPHA * (reward + GAMMA * best_next - old_q)


episode_rewards = []

for episode in range(EPISODES):

    total_reward = 0
    step = 0
    traci.start(SUMO_CONFIG)

    while step < TOTAL_STEPS:
        state = get_state(tls_id, detector_ids, crossing_ids)
        action = choose_action(state)
        
        step = perform_action(tls_id, step, TOTAL_STEPS, action)

        next_state = get_state(tls_id, detector_ids, crossing_ids)
        reward = get_reward(get_all_waiting_vehicles(detector_ids), get_all_waiting_peds(crossing_ids))
        total_reward += reward
        update_q(state, action, reward, next_state)

        print(f'Step: {step}, State: {state}, Action: {action}, Reward: {reward}')

    traci.close()

    episode_rewards.append(total_reward)
    EPSILON = max(EPSILON_MIN, EPSILON * EPSILON_DECAY)

    print(f'Episode: {episode + 1}, Total Reward: {total_reward}, Epsilon: {EPSILON}')

with open('./q_learning.txt', 'w') as f:
    f.write(str(episode_rewards) + '\n' + str(Q))