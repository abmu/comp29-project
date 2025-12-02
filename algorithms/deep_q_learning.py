import torch
import torch.nn as nn
import random
from collections import deque


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

    def forward(self, x: tuple[int, ...]):
        return self.model(x)
    

"""
    Replay buffer memory
"""
class ReplayBuffer:
    def __init__(self, capacity: int = 1024):
        self.buffer = deque(maxlen=capacity)

    def push(self, state: tuple[int, ...], action: int, reward: float, next_state: tuple[int, ...], duration: int, done: bool):
        self.buffer.append((state, action, reward, next_state, duration, done))

    def sample(self, batch_size: int):
        batch = random.sample(self.buffer, batch_size)
        