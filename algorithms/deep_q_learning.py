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
from environment import SUMO_CONFIG, TOTAL_STEPS, tls_id, queue_ids, crossing_ids, ACTION_SPACE, get_state, perform_action


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

    def push(self, state: tuple[int, ...], action: int, reward: float, next_state: tuple[int, ...], duration: float, done: bool) -> None:
        self.buffer.append((state, action, reward, next_state, duration, done))

    def sample(self, batch_size: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, durations, dones = map(np.array, zip(*batch))
        return states, actions, rewards, next_states, durations, dones
    
    def __len__(self) -> int:
        return len(self.buffer)


class DeepQLearning:
    def __init__(self, results_dir: str, train_mode: bool = False) -> None:
        self.results_dir = results_dir
        self.train_mode = train_mode
        self.model_name = 'dpn_model.pt'

        self.learning_rate = 0.0005
        self.batch_size = 64
        self.target_update = 20  # episodes
        self.gamma = 0.9  # discount factor
        self.epsilon = 1.0  # exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.005

        traci.start(SUMO_CONFIG, label='deep_q_learning')
        conn = traci.getConnection('deep_q_learning')
        state_size = len(get_state(conn, tls_id, queue_ids, crossing_ids))
        conn.close()
        action_size = len(ACTION_SPACE)

        self.policy_net = DQN(state_size, action_size)
        if not self.train_mode:
            self.policy_net.load_state_dict(torch.load(self.results_dir + self.model_name))
            self.policy_net.eval()
            self.epsilon = 0
            self.epsilon_min = 0

        self.target_net = DQN(state_size, action_size)
        self.target_net.load_state_dict(self.policy_net.state_dict())

        self.optimiser = optim.Adam(self.policy_net.parameters(), lr=self.learning_rate)
        self.memory = ReplayBuffer()
    

    def choose_action(self, state: tuple[int, ...]) -> int:
        # choose action using an epsilon-greedy policy
        actions = list(ACTION_SPACE.keys())
        if random.random() < self.epislon:
            # exploration - choose random action
            return random.choice(actions)
        else:
            # exploitation - using DQN
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            with torch.no_grad():
                q_values = self.policy_net(state_tensor)
            nn_index = torch.argmax(q_values).item()
            return actions[nn_index]


    def train_step(self) -> None:
        # perform a train step of the policy network
        if len(self.memory) < self.batch_size:
            return

        states, actions, rewards, next_states, durations, dones = self.memory.sample(self.batch_size)

        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions).unsqueeze(1)
        rewards = torch.FloatTensor(rewards).unsqueeze(1)
        next_states = torch.FloatTensor(next_states)
        durations = torch.FloatTensor(durations).unsqueeze(1)
        dones = torch.FloatTensor(dones.astype(np.float32)).unsqueeze(1)

        # Q(s,a)
        q_values = self.policy_net(states).gather(1, actions)

        # Target Q(s',a')
        with torch.no_grad():
            next_q_values = self.target_net(next_states).max(dim=1)[0].unsqueeze(1)
            # Use duration for SMDP effect
            target = rewards + (1 - dones) * (self.gamma ** durations) * next_q_values

        loss = nn.MSELoss()(q_values, target)
        self.optimiser.zero_grad()
        loss.backward()
        self.optimiser.step()


    def run(self, epoch: int = 1) -> tuple[float, float]:
        # run a single episode and return the reward
        total_reward = 0
        step = 0

        traci.start(SUMO_CONFIG, label='deep_q_learning')
        conn = traci.getConnection('deep_q_learning')

        try:
            while step < TOTAL_STEPS:
                state = get_state(conn, tls_id, queue_ids, crossing_ids)
                action = self.choose_action(state)
                
                step, reward, duration = perform_action(conn, tls_id, step, TOTAL_STEPS, action)

                next_state = get_state(conn, tls_id, queue_ids, crossing_ids)
                done = step >= TOTAL_STEPS
                total_reward += reward

                # save transition
                action_id_to_idx = {aid: i for i, aid in enumerate(ACTION_SPACE.keys())}
                action_idx = action_id_to_idx[action]
                self.memory.push(state, action_idx, reward, next_state, duration, done)

                if self.train_mode:
                    self.train_step()

        except Exception as e:
            raise
        finally:
            conn.close()

            self.epislon = max(self.epsilon_min, self.epislon * self.epsilon_decay)

            if self.train_mode:
                torch.save(self.policy_net.state_dict(), self.results_dir + self.model_name)
                if (epoch) % self.target_update == 0:
                    self.target_net.load_state_dict(self.policy_net.state_dict())
                    print("Target network updated")

        return total_reward
