import os
import sys
import uuid
import math

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

import numpy as np
import random
from runner import Runner
from environment import TOTAL_STEPS, ACTION_SPACE, Controller, simulation_step, get_state
from utils import file_dump, file_eval


class QLearning(Runner):
    def __init__(self, tls_id: str, sumo_cfg: str, save_dir: str, train_mode: bool, compress_state: bool = True) -> None:
        self.tls_id = tls_id
        self.sumo_cfg = sumo_cfg
        self.save_dir = save_dir
        self.train_mode = train_mode
        self.compress_state = compress_state
        self.table_name = 'q_table.txt'
        if not self.compress_state:
            self.table_name = 'uncompressed_' + self.table_name

        self.q = {} # {(state, action): value}
        self.t = 0

        # Q-learning hyperparameters
        self.alpha = 0.1 # learning rate
        self.gamma = 0.9 # discount factor
        self.epsilon_decay = 1.5e-6
        self.epsilon_max = 1.0
        self.epsilon_min = 0.01

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
        actions = list(ACTION_SPACE.keys())
        if self.train_mode and random.random() < self.epsilon:
            # exploration - choose random action
            return random.choice(actions)
        else:
            # exploitation - choose action with highest Q-value
            qs = [self.get_q(state, a) for a in actions]
            return actions[np.argmax(qs)]


    def update_q(self, state: tuple[int, ...], action: int, reward: float, next_state: tuple[int, ...], duration: float) -> None:
        # update Q-value of state and action combination based on reward and next state
        actions = list(ACTION_SPACE.keys())
        old_q = self.get_q(state, action)
        best_next = max(self.get_q(next_state, a) for a in actions)
        # Semi-Markov Decision Process
        self.q[(state, action)] = old_q + self.alpha * (reward + (self.gamma ** duration) * best_next - old_q)


    def run(self, epoch: int = 1) -> tuple[float, float]:
        # run a single episode and return the reward
        total_reward = 0
        step = 0
        
        tid = str(uuid.uuid4())
        traci.start(self.sumo_cfg, label=tid)
        conn = traci.getConnection(tid)

        controller = Controller(conn, self.tls_id)

        try:
            while step < TOTAL_STEPS:
                if controller.finished():
                    state = get_state(conn, self.tls_id, self.compress_state)
                    action = self.choose_action(state)
                    controller.set_action(action)
                
                simulation_step(conn)
                reward = controller.run()
                total_reward += reward
                step += 1
                self.t += 1
    
                if controller.finished() and self.train_mode:
                    next_state = get_state(conn, self.tls_id, self.compress_state)
                    duration = controller.get_total_duration()
                    self.update_q(state, action, reward, next_state, duration)
                
        except Exception as e:
            raise
        finally:
            conn.close()

            if self.train_mode:
                file_dump(self.save_dir + self.table_name, str(self.q))

        return total_reward
