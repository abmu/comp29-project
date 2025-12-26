import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

from environment import TOTAL_STEPS, get_state, perform_action, compute_stats, get_cache
from utils import file_dump


class FixedTimer:
    def __init__(self, tls_id: str, sumo_cfg: str, save_dir: str, stats_mode: bool) -> None:
        self.tls_id = tls_id
        self.sumo_cfg = sumo_cfg
        self.save_dir = save_dir
        self.stats_mode = stats_mode
        self.stats_name = 'cache_stats.txt'
        self.action_loop = [0,0,0,3,3,3,6]


    def run(self, epoch: int = 1) -> float:
        # run a single episode and return the reward
        total_reward = 0
        curr_idx = 0
        step = 0
        
        traci.start(self.sumo_cfg, label='fixed_timer')
        conn = traci.getConnection('fixed_timer')

        try:
            while step < TOTAL_STEPS:
                state = get_state(conn, self.tls_id)
                action = self.action_loop[curr_idx]

                step, reward, _ = perform_action(conn, self.tls_id, step, action)

                curr_idx = (curr_idx + 1) % len(self.action_loop)
                total_reward += reward

        except Exception as e:
            raise
        finally:
            conn.close()

            if self.stats_mode:
                file_dump(self.save_dir + self.stats_name, str(compute_stats(get_cache())))

        return total_reward
