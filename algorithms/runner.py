import os
import sys
import uuid

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

from environment import TOTAL_STEPS, Controller, simulation_step, compute_stats, get_cache
from utils import file_dump


class Runner:
    def __init__(self, tls_id: str, sumo_cfg: str, save_dir: str, stats_mode: bool) -> None:
        self.tls_id = tls_id  # technically this could just be a connected junction with no traffic light -- not a tls!
        self.sumo_cfg = sumo_cfg
        self.save_dir = save_dir
        self.stats_mode = stats_mode
        self.stats_name = 'cache_stats.txt'


    def run(self, epoch: int = 1) -> float:
        # run a single episode and return the reward
        total_reward = 0
        step = 0
        
        tid = str(uuid.uuid4())
        traci.start(self.sumo_cfg, label=tid)
        conn = traci.getConnection(tid)

        controller = Controller(conn, self.tls_id)

        try:
            while step < TOTAL_STEPS:
                simulation_step(conn)
                reward = controller.run()
                total_reward += reward
                step += 1

        except Exception as e:
            raise
        finally:
            conn.close()

            if self.stats_mode:
                file_dump(self.save_dir + self.stats_name, str(compute_stats(get_cache())))

        return total_reward
