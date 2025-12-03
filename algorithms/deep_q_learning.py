import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque
from environment import SUMO_CONFIG, TOTAL_STEPS, tls_id, queue_ids, crossing_ids, ACTION_SPACE, get_state, perform_action, set_route


TRAIN_MODE = False

RESULTS_FILE = 'results/deep_q_learning.txt'

SEED = 29

LEARNING_RATE = 0.0005
BATCH_SIZE = 64
TARGET_UPDATE = 20  # episodes
GAMMA = 0.9 # discount factor
EPSILON = 1.0 # exploration rate
EPSILON_DECAY = 0.995
EPSILON_MIN = 0.005

EPISODES = 1000

if not TRAIN_MODE:
    EPSILON = EPSILON_MIN


"""
    Deep Q-Network model
"""
class DQN(nn.Module):
    def __init__(self, state_dim: int, action_dim: int):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)
    

"""
    Replay buffer memory
"""
class ReplayBuffer:
    def __init__(self, capacity: int = 16384):
        self.buffer = deque(maxlen=capacity)

    def push(self, state: tuple[int, ...], action: int, reward: float, next_state: tuple[int, ...], duration: int, done: bool) -> None:
        self.buffer.append((state, action, reward, next_state, duration, done))

    def sample(self, batch_size: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, durations, dones = map(np.array, zip(*batch))
        return states, actions, rewards, next_states, durations, dones
    
    def __len__(self) -> int:
        return len(self.buffer)


state_size = len(get_state(tls_id, queue_ids, crossing_ids))
action_size = len(ACTION_SPACE)

policy_net = DQN(state_size, action_size)
target_net = DQN(state_size, action_size)
target_net.load_state_dict(policy_net.state_dict())

optimiser = optim.Adam(policy_net.parameters(), lr=LEARNING_RATE)
memory = ReplayBuffer()



....
OLD Q-LEARNING CODE
...

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


def update_q(state: tuple[int, ...], action: int, reward: float, next_state: tuple[int, ...], duration: int) -> None:
    # update Q-value of state and action combinatoin based on reward and next state
    actions = list(ACTION_SPACE.keys())
    old_q = get_q(state, action)
    best_next = max(get_q(next_state, a) for a in actions)
    # Semi-Markov Decision Process
    Q[(state, action)] = old_q + ALPHA * (reward + (GAMMA ** duration) * best_next - old_q)


episode_rewards = []

random.seed(SEED)

for episode in range(EPISODES):

    print(f'Episode: {episode + 1}')
    
    # set SUMO route
    set_route(episode+1)

    print(f'Running SUMO...')

    # run episode training
    total_reward = 0
    step = 0
    traci.start(SUMO_CONFIG)

    while step < TOTAL_STEPS:
        state = get_state(tls_id, queue_ids, crossing_ids)
        action = choose_action(state)
        
        step, reward, step_delta = perform_action(tls_id, step, TOTAL_STEPS, action)

        next_state = get_state(tls_id, queue_ids, crossing_ids)
        total_reward += reward
        update_q(state, action, reward, next_state, step_delta)

        # print(f'Step: {step}, State: {state}, Action: {action}, Reward: {reward}')

    traci.close()

    episode_rewards.append(total_reward)
    EPSILON = max(EPSILON_MIN, EPSILON * EPSILON_DECAY)

    print(f'Total Reward: {total_reward}, Epsilon: {EPSILON}\n')
    if TRAIN_MODE:
        file_dump(RESULTS_FILE, str(episode_rewards))
        file_dump(Q_TABLE_FILE, str(Q))