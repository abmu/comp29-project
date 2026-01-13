import math
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque
from agent import Runner
from environment import ACTION_SPACE, get_state, get_blank_state


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


class DeepQLearning(Runner):
    def __init__(self, tls_id: str, save_dir: str, train_mode: bool, compress_state: bool = False) -> None:
        super().__init__(tls_id, save_dir)
        self.controller = None
        self.train_mode = train_mode
        self.compress_state = compress_state
        self.model_name = f'dqn_model_{tls_id}.pt'
        if not self.compress_state:
            self.model_name = 'uncompressed_' + self.model_name
        self.t = 0

        self.learning_rate = 0.0005
        self.batch_size = 64
        self.target_update = 72000  # steps
        self.gamma = 0.9  # discount factor
        self.epsilon_decay = 1.5e-6
        self.epsilon_max = 1.0
        self.epsilon_min = 0.01

        self.initialised = False


    def get_state_size(self) -> int:
        # return the input state size for the policy net
        return len(get_blank_state(self.tls_id, self.compress_state))


    def initialise(self) -> None:
        # initialise neural networks
        state_size = self.get_state_size()
        action_size = len(ACTION_SPACE)

        self.policy_net = DQN(state_size, action_size)
        if not self.train_mode:
            self.policy_net.load_state_dict(torch.load(self.save_dir + self.model_name))
            self.policy_net.eval()
            self.t = float('inf')
            self.epsilon_min = 0

        self.target_net = DQN(state_size, action_size)
        self.target_net.load_state_dict(self.policy_net.state_dict())

        self.optimiser = optim.Adam(self.policy_net.parameters(), lr=self.learning_rate)
        self.memory = ReplayBuffer()

        self.initialised = True
    

    @property
    def epsilon(self) -> float:
        """
        Get the exponential decay epsilon value (exploration rate)

        Returns:
            The epsilon value
        """
        return self.epsilon_min + (self.epsilon_max - self.epsilon_min) * math.exp(-self.epsilon_decay * self.t)
    

    def choose_action(self, state: tuple[int, ...]) -> int:
        # choose action using an epsilon-greedy policy
        actions = list(ACTION_SPACE.keys())
        if self.train_mode and random.random() < self.epsilon:
            # exploration - choose random action
            return random.choice(actions)
        else:
            # exploitation - using DQN
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            with torch.no_grad():
                q_values = self.policy_net(state_tensor)
            nn_index = torch.argmax(q_values).item()
            return actions[nn_index]


    def train_policy_net(self) -> None:
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


    def start_episode(self, conn) -> None:
        super().start_episode(conn)
        if not self.initialised:
            self.initialise()


    def start_step(self):
        if self.controller.finished():
            self.state = get_state(self.conn, self.tls_id, self.compress_state)
            self.action = self.choose_action(self.state)
            self.reward = 0
            self.controller.set_action(self.action)


    def run(self) -> float:
        self.t += 1
        if self.train_mode and self.t % self.target_update == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
            # print("Target network updated")
        reward = self.controller.run()
        self.reward += reward
        return reward


    def finish_step(self, done: bool):
        if self.train_mode and self.controller.finished():
            next_state = get_state(self.conn, self.tls_id, self.compress_state)
            duration = self.controller.get_total_duration()

            # save transition
            action_id_to_idx = {aid: i for i, aid in enumerate(ACTION_SPACE.keys())}
            action_idx = action_id_to_idx[self.action]
            self.memory.push(self.state, action_idx, self.reward, next_state, duration, done)

            self.train_policy_net()

    
    def finish_episode(self):
        if self.train_mode:
            torch.save(self.policy_net.state_dict(), self.save_dir + self.model_name)
