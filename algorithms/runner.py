import os
import sys
import uuid

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

from environment import Controller, compute_stats, get_cache
from utils import file_dump


class Runner:
    def __init__(self, tls_id: str, save_dir: str, stats_mode: bool) -> None:
        self.tls_id = tls_id  # technically this could just be a connected junction with no traffic light -- not a tls!
        self.save_dir = save_dir
        self.stats_mode = stats_mode
        self.stats_name = 'cache_stats.txt'
        self.controller = None


    def start_episode(self, conn) -> None:
        # run at the start of every episode
        self.controller = Controller(conn, self.tls_id)


    def start_step(self, conn, t: int) -> None:
        # run at the start of every step
        pass

    
    def run(self) -> float:
        # run during each step
        return self.controller.run()
    

    def finish_step(self, t: int) -> None:
        # run at the end of every step
        pass

    
    def finish_episode(self) -> None:
        # run at the end of every episode
        if self.stats_mode:
            file_dump(self.save_dir + self.stats_name, str(compute_stats(get_cache())))
