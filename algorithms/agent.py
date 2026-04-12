from abc import ABC, abstractmethod
from environment import Controller, compute_stats, get_cache
from utils import file_dump


class Runner(ABC):
    def __init__(self, tls_id: str, save_dir: str) -> None:
        self.tls_id = tls_id  # technically this could just be a connected junction with no traffic light -- not a tls!
        self.save_dir = save_dir
        self.conn = None
        self.controller = None


    def start_episode(self, conn, offset: float = 0) -> None:
        # run at the start of every episode
        self.conn = conn
        self.controller = Controller(conn, self.tls_id, offset=offset)


    @abstractmethod
    def start_step(self) -> None:
        # run at the start of every step
        pass

    
    def run(self) -> float:
        # run during each step
        return self.controller.run()
    

    @abstractmethod
    def finish_step(self, done: bool) -> None:
        # run at the end of every step
        pass

    
    @abstractmethod
    def finish_episode(self) -> None:
        # run at the end of every episode
        pass


class DefaultRunner(Runner):
    def __init__(self, tls_id: str, save_dir: str, stats_mode: bool) -> None:
        super().__init__(tls_id, save_dir)
        self.stats_mode = stats_mode
        self.stats_name = f'cache_stats__{tls_id}.txt'


    def start_episode(self, conn) -> None:
        self.conn = conn
        self.controller = Controller(conn, self.tls_id, self.stats_mode)


    def start_step(self):
        pass


    def finish_step(self, done: bool):
        pass

    
    def finish_episode(self):
        if self.stats_mode:
            file_dump(self.save_dir + self.stats_name, str(compute_stats(get_cache())))