import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

from environment import SUMO_CONFIG, TOTAL_STEPS, tls_id, queue_ids, crossing_ids, get_state, perform_action, compute_stats, get_cache
from utils import file_dump


class FixedTimer:
    def __init__(self, results_dir: str, stats_mode: bool) -> None:
        self.results_dir = results_dir
        self.stats_mode = stats_mode
        self.stats_name = 'cache_stats.txt'
        self.action_loop = [0,0,0,3,3,3,6]


    def run(self, epoch: int = 1) -> float:
        # run a single episode and return the reward
        total_reward = 0
        curr_idx = 0
        step = 0
        
        traci.start(SUMO_CONFIG, label='fixed_timer')
        conn = traci.getConnection('fixed_timer')

        try:
            while step < TOTAL_STEPS:
                state = get_state(conn, tls_id, queue_ids, crossing_ids)
                action = self.action_loop[curr_idx]

                step, reward, _ = perform_action(conn, tls_id, step, TOTAL_STEPS, action)

                curr_idx = (curr_idx + 1) % len(self.action_loop)
                total_reward += reward

        except Exception as e:
            raise
        finally:
            conn.close()

            if self.stats_mode:
                file_dump(self.results_dir + self.stats_name, str(compute_stats(get_cache())))

        return total_reward
