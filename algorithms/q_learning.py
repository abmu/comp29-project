import math
import numpy as np
import random
from agent import Runner
from environment import ACTION_SPACE, get_state
from utils import file_dump, file_eval


class QLearning(Runner):
    def __init__(self, tls_id: str, save_dir: str, train_mode: bool, compression_level: int = 2, seed: int = 0) -> None:
        super().__init__(tls_id, save_dir)
        self.controller = None
        self.train_mode = train_mode
        self.compression_level = compression_level
        self.rng = random.Random(seed)
        self.table_name = f'q_table__c{compression_level}__{tls_id}.txt'
        self.t = 0
        self.reward = 0

        # Q-learning hyperparameters
        self.alpha = 0.1 # learning rate
        self.gamma = 0.9 # discount factor
        self.epsilon_decay = 1.5e-6 # 1.5e-7
        self.epsilon_max = 1.0
        self.epsilon_min = 0.01

        self.q = {} # {(state, action): value}
        if not self.train_mode:
            self.q = file_eval(self.save_dir + self.table_name)[0]
            self.t = float('inf')
            self.epsilon_min = 0


    def get_q(self, state: tuple[int, ...], action: int) -> float:
        # return Q-value of state and action combination
        return self.q.get((state, action), 0.0)


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
        actions = sorted(ACTION_SPACE.keys())
        if self.train_mode and self.rng.random() < self.epsilon:
            # exploration - choose random action
            return self.rng.choice(actions)
        else:
            # exploitation - choose action with highest Q-value
            qs = [self.get_q(state, a) for a in actions]
            return actions[np.argmax(qs)]


    def update_q(self, state: tuple[int, ...], action: int, reward: float, next_state: tuple[int, ...], duration: float) -> None:
        # update Q-value of state and action combination based on reward and next state
        actions = sorted(ACTION_SPACE.keys())
        old_q = self.get_q(state, action)
        best_next = max(self.get_q(next_state, a) for a in actions)
        # Semi-Markov Decision Process
        self.q[(state, action)] = old_q + self.alpha * (reward + (self.gamma ** duration) * best_next - old_q)


    def start_step(self):
        if self.controller.finished():
            self.state = get_state(self.conn, self.tls_id, self.compression_level)
            self.action = self.choose_action(self.state)
            self.reward = 0
            self.controller.set_action(self.action)


    def run(self) -> float:
        self.t += 1
        reward = self.controller.run()
        self.reward += reward
        return reward


    def finish_step(self, done: bool):
        if self.train_mode and self.controller.finished() and self.controller.initialised:
            next_state = get_state(self.conn, self.tls_id, self.compression_level)
            duration = self.controller.get_total_duration()
            self.update_q(self.state, self.action, self.reward, next_state, duration)

    
    def finish_episode(self):
        if self.train_mode:
            file_dump(self.save_dir + self.table_name, str(self.q))

