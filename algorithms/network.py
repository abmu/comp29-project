import os
import sys
import uuid

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

from runner import Runner
from environment import TOTAL_STEPS, ACTION_SPACE, get_state, perform_action


class Controller:
    def __init__(self):
        self.action = 0
        self.duration = 10
        self.next = []

    def __str__(self):
        return f'{self.action}, {self.duration}, {self.next}'

    def finished(self):
        return not self.duration and not self.next
    
    def set_action(self, new_action, new_dur, next = []):
        self.action = new_action
        self.duration = new_dur
        self.next = next.copy()

    def run(self):
        self.duration -= 1
        if not self.duration:
            if not self.next:
                return
            self.action, self.duration = self.next.pop(0)


class Network(Runner):
    def __init__(self, tls_id: str, sumo_cfg: str) -> None:
        self.tls_id = tls_id
        self.sumo_cfg = sumo_cfg
        self.controller = Controller()
        self.action_loop = [0,0,0,3,3,3,6]


    def run(self, epoch: int = 1) -> float:
        # run a single episode and return the reward
        total_reward = 0
        curr_idx = 0
        step = 0
        
        tid = str(uuid.uuid4())
        traci.start(self.sumo_cfg, label=tid)
        conn = traci.getConnection(tid)

        try:
            while step < TOTAL_STEPS:
                state = get_state(conn, self.tls_id)
                action = self.action_loop[curr_idx]

                if self.controller.finished():
                    curr_idx = (curr_idx + 1) % len(self.action_loop)
                    duration, phase_switch = ACTION_SPACE[action].values()
                    self.controller.set_action(action, duration, phase_switch)
                else:
                    self.controller.run()

                
                # step, reward, _ = perform_action(conn, self.tls_id, step, action, self.stats_mode)

                # total_reward += reward

                step += 1

        except Exception as e:
            print(e)
            raise
        finally:
            conn.close()

        return total_reward
