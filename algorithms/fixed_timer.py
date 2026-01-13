from agent import Runner
from environment import compute_stats, get_cache
from utils import file_dump


class FixedTimer(Runner):
    def __init__(self, tls_id: str, save_dir: str, stats_mode: bool) -> None:
        super().__init__(tls_id, save_dir)
        self.controller = None
        self.stats_mode = stats_mode
        self.stats_name = f'{tls_id}_cache_stats.txt'

        self.action_loop = [0,0,0,3,3,3,6]


    def start_episode(self, conn):
        super().start_episode(conn)
        self.curr_idx = 0
        

    def start_step(self) -> None:
        if self.controller.finished():
            action = self.action_loop[self.curr_idx]
            self.controller.set_action(action)
            self.curr_idx = (self.curr_idx + 1) % len(self.action_loop)


    def finish_step(self, done: bool):
        pass

    
    def finish_episode(self):
        if self.stats_mode:
            file_dump(self.save_dir + self.stats_name, str(compute_stats(get_cache())))