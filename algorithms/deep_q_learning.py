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
from utils import file_dump


TRAIN_MODE = True

RESULTS_FILE = 'results/deep_q_learning.txt'
MODEL_FILE = 'results/dqn_model.pt'

SEED = 29

LEARNING_RATE = 0.0005
BATCH_SIZE = 64
TARGET_UPDATE = 20  # episodes
GAMMA = 0.9  # discount factor
EPSILON = 1.0  # exploration rate
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


traci.start(SUMO_CONFIG)
state_size = len(get_state(tls_id, queue_ids, crossing_ids))
traci.close()
action_size = len(ACTION_SPACE)

policy_net = DQN(state_size, action_size)
if not TRAIN_MODE:
    policy_net.load_state_dict(torch.load(MODEL_FILE))
    policy_net.eval()
    EPSILON = 0
    EPSILON_MIN = 0

target_net = DQN(state_size, action_size)
target_net.load_state_dict(policy_net.state_dict())

optimiser = optim.Adam(policy_net.parameters(), lr=LEARNING_RATE)
memory = ReplayBuffer()

ACTION_IDS = sorted(ACTION_SPACE.keys())
ACTION_ID_TO_IDX = {aid: i for i, aid in enumerate(ACTION_IDS)}


def choose_action(state: tuple[int, ...]) -> int:
    # choose action using an epsilon-greedy policy
    if random.random() < EPSILON:
        # exploration - choose random action
        return random.choice(ACTION_IDS)
    else:
        # exploitation - using DQN
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            q_values = policy_net(state_tensor)
        nn_index = torch.argmax(q_values).item()
        return ACTION_IDS[nn_index]


def train_step() -> None:
    # perform a train step of the policy network
    if len(memory) < BATCH_SIZE:
        return

    states, actions, rewards, next_states, durations, dones = memory.sample(BATCH_SIZE)

    states = torch.FloatTensor(states)
    actions = torch.LongTensor(actions).unsqueeze(1)
    rewards = torch.FloatTensor(rewards).unsqueeze(1)
    next_states = torch.FloatTensor(next_states)
    durations = torch.FloatTensor(durations).unsqueeze(1)
    dones = torch.FloatTensor(dones.astype(np.float32)).unsqueeze(1)

    # Q(s,a)
    q_values = policy_net(states).gather(1, actions)

    # Target Q(s',a')
    with torch.no_grad():
        next_q_values = target_net(next_states).max(dim=1)[0].unsqueeze(1)
        # Use duration for SMDP effect
        target = rewards + (1 - dones) * (GAMMA ** durations) * next_q_values

    loss = nn.MSELoss()(q_values, target)
    optimiser.zero_grad()
    loss.backward()
    optimiser.step()


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
        
        step, reward, duration = perform_action(tls_id, step, TOTAL_STEPS, action)

        next_state = get_state(tls_id, queue_ids, crossing_ids)
        done = step >= TOTAL_STEPS
        total_reward += reward

        # save transition
        action_idx = ACTION_ID_TO_IDX[action]
        memory.push(state, action_idx, reward, next_state, duration, done)

        if TRAIN_MODE:
            train_step()

        # print(f'Step: {step}, State: {state}, Action: {action}, Reward: {reward}')

    traci.close()

    episode_rewards.append(total_reward)

    if TRAIN_MODE and (episode + 1) % TARGET_UPDATE == 0:
        target_net.load_state_dict(policy_net.state_dict())
        print("Target network updated")

    EPSILON = max(EPSILON_MIN, EPSILON * EPSILON_DECAY)

    print(f'Total Reward: {total_reward}, Epsilon: {EPSILON}\n')
    if TRAIN_MODE:
        file_dump(RESULTS_FILE, str(episode_rewards))
        torch.save(policy_net.state_dict(), MODEL_FILE)