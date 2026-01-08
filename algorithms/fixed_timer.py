import os
import sys
import uuid

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

from runner import Runner
from environment import TOTAL_STEPS, Controller, get_state, simulation_step, compute_stats, get_cache
from utils import file_dump


class FixedTimer(Runner):
    def __init__(self, tls_id: str, save_dir: str, stats_mode: bool) -> None:
        self.tls_id = tls_id
        self.save_dir = save_dir
        self.stats_mode = stats_mode
        self.stats_name = 'cache_stats.txt'
        self.action_loop = [0,0,0,3,3,3,6]
        self.controller = None

    def start_step(self, conn, t: int) -> None:
        if self.controller.finished():
            state = get_state(conn, self.tls_id)
            action = self.action_loop[curr_idx]
            self.controller.set_action(action)
            curr_idx = (curr_idx + 1) % len(self.action_loop)
