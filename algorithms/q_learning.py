import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

import numpy as np
import random
from environment import SUMO_CONFIG, TOTAL_STEPS, tls_id, queue_ids, crossing_ids, ACTION_SPACE, get_state, perform_action
from utils import file_dump, file_eval


class QLearning:
    def __init__(self, results_dir: str, train_mode: bool) -> None:
        self.results_dir = results_dir
        self.train_mode = train_mode
        self.table_name = 'q_table.txt'

        self.q = {} # {(state, action): value}

        # Q-learning hyperparameters
        self.alpha = 0.1 # learning rate
        self.gamma = 0.9 # discount factor
        self.epsilon = 1.0 # exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.005

        if not self.train_mode:
            self.q = file_eval(self.results_dir + self.table_name)[0]
            self.epislon = 0
            self.epsilon_min = 0


    def get_q(self, state: tuple[int, ...], action: int) -> float:
        # return Q-value of state and action combination
        return self.q.get((state, action), 0.0)


    def choose_action(self, state: tuple[int, ...]) -> int:
        # choose action using an epsilon-greedy policy
        actions = list(ACTION_SPACE.keys())
        if random.random() < self.epislon:
            # exploration - choose random action
            return random.choice(actions)
        else:
            # exploitation - choose action with highest Q-value
            qs = [self.get_q(state, a) for a in actions]
            return actions[np.argmax(qs)]


    def update_q(self, state: tuple[int, ...], action: int, reward: float, next_state: tuple[int, ...], duration: float) -> None:
        # update Q-value of state and action combinatoin based on reward and next state
        actions = list(ACTION_SPACE.keys())
        old_q = self.get_q(state, action)
        best_next = max(self.get_q(next_state, a) for a in actions)
        # Semi-Markov Decision Process
        self.q[(state, action)] = old_q + self.alpha * (reward + (self.gamma ** duration) * best_next - old_q)


    def run(self, epoch: int = 1) -> tuple[float, float]:
        # run a single episode and return the reward
        total_reward = 0
        step = 0
        
        traci.start(SUMO_CONFIG, label='q_learning')
        conn = traci.getConnection('q_learning')

        try:
            while step < TOTAL_STEPS:
                state = get_state(conn, tls_id, queue_ids, crossing_ids)
                action = self.choose_action(state)
                
                step, reward, duration = perform_action(conn, tls_id, step, TOTAL_STEPS, action)

                next_state = get_state(conn, tls_id, queue_ids, crossing_ids)
                total_reward += reward

                if self.train_mode:
                    self.update_q(state, action, reward, next_state, duration)

        except Exception as e:
            raise
        finally:
            conn.close()

            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

            if self.train_mode:
                file_dump(self.results_dir + self.table_name, str(self.q))

        return total_reward
