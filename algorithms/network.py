import os
import sys
import uuid

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

from environment import TOTAL_STEPS, Controller, get_state, simulation_step


class Network:
    def __init__(self, tls_id: str, sumo_cfg: str) -> None:
        self.tls_id = tls_id
        self.sumo_cfg = sumo_cfg
        self.action_loop = [0,0,0,3,3,3,6]


    def run(self, epoch: int = 1) -> float:
        # run a single episode and return the reward
        total_reward = 0
        curr_idx = 0
        step = 0
        
        tid = str(uuid.uuid4())
        traci.start(self.sumo_cfg, label=tid)
        conn = traci.getConnection(tid)

        controller = Controller(conn, self.tls_id, action=curr_idx)

        try:
            while step < TOTAL_STEPS:
                state = get_state(conn, self.tls_id)

                if controller.finished():
                    curr_idx = (curr_idx + 1) % len(self.action_loop)
                    action = self.action_loop[curr_idx]
                    controller.set_action(action)

                simulation_step(conn)
                reward = controller.run()
                total_reward += reward
                step += 1

        except Exception as e:
            raise
        finally:
            conn.close()

        return total_reward
