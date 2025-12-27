import random
import multiprocessing as mp
from pathlib import Path
from environment import get_sumo_cfg, set_route
from runner import Runner
from fixed_timer import FixedTimer
# from q_learning import QLearning
# from deep_q_learning import DeepQLearning
from utils import file_dump


SEED = 29  # may not work well with multiple parallel processes -- non-determinism of execution

DIR_PREFIX = '../simulation/'
NET_NAME = 'demo'
TLS_ID = 'CJ_1'  # traffic light system ID
MODE = 'train'  # 'train' or 'eval'

RESULTS_DIR = f'results/{NET_NAME}/'

ALGORITHMS = {
    # Get cache stats used to calculate reward weights
    'fixed_timer': FixedTimer(
        tls_id=TLS_ID,
        sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME),
        save_dir=RESULTS_DIR,
        stats_mode=True
    ),



    # 'fixed_timer': FixedTimer(
    #     tls_id=TLS_ID,
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME),
    #     save_dir=RESULTS_DIR,
    #     stats_mode=False
    # ),
    # 'q_learning': QLearning(
    #     tls_id=TLS_ID,
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME),
    #     save_dir=RESULTS_DIR,
    #     train_mode=(MODE == 'train'),
    #     compress_state=True
    # ),
    # 'deep_q_learning': DeepQLearning(
    #     tls_id=TLS_ID,
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME),
    #     save_dir=RESULTS_DIR,
    #     train_mode=(MODE == 'train'),
    #     compress_state=True
    # ),
    # 'q_learning': QLearning(
    #     tls_id=TLS_ID,
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME),
    #     save_dir=RESULTS_DIR,
    #     train_mode=(MODE == 'train'),
    #     compress_state=False
    # ),
    # 'deep_q_learning': DeepQLearning(
    #     tls_id=TLS_ID,
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME),
    #     save_dir=RESULTS_DIR,
    #     train_mode=(MODE == 'train'),
    #     compress_state=False
    # ),



    # 'zebra': Runner(
    #     tls_id=TLS_ID,
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME, netfile='main'),
    #     save_dir=RESULTS_DIR,
    #     stats_mode=False
    # ),
    # 'fixed_timer': FixedTimer(
    #     tls_id=TLS_ID,
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME, netfile='tls'),
    #     save_dir=RESULTS_DIR,
    #     stats_mode=False
    # ),
    # 'deep_q_learning': DeepQLearning(
    #     tls_id=TLS_ID,
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME, netfile='tls'),
    #     save_dir=RESULTS_DIR,
    #     train_mode=(MODE == 'train'),
    #     compress_state=True
    # ),
}


def run_ep(args: tuple[str, int]) -> tuple[str, float]:
    """
    Run an episode using the specified algorithm
    """
    alg, epoch = args
    try:
        reward = ALGORITHMS[alg].run(epoch)
        return alg, reward
    except Exception as e:
        print(f'[{alg}] [{epoch}] exception: {e}')
        return alg, None


if __name__ == "__main__":
    random.seed(SEED)

    episode_rewards = {a: [] for a in ALGORITHMS}
    
    # create a process pool
    pool = mp.Pool(processes=len(ALGORITHMS))

    routes_dir = Path(f'{DIR_PREFIX}routes/{NET_NAME}/{MODE}/').glob('*')
    count = sum(1 if f.is_dir() else 0 for f in routes_dir)  # count the number of folders in the routes directory
    print(f'Using {count} "{MODE}" routes for the network "{NET_NAME}"...')

    for episode in range(1, count+1):
        print(f'\n=== Episode: {episode} ===')
        
        # set SUMO route
        set_route(episode, dirprefix=DIR_PREFIX, netname=NET_NAME, mode=MODE)

        # run algorithms in parallel
        print(f'Running {len(ALGORITHMS)} instances of SUMO...')
        jobs = [(algorithm, episode) for algorithm in ALGORITHMS]
        results = pool.map(run_ep, jobs)

        for algorithm, reward in results:
            print(f'[{algorithm}] reward = {reward}')

            episode_rewards[algorithm].append(reward)

            # save to file
            fname = f'{RESULTS_DIR}{MODE}/{algorithm}.txt'
            file_dump(fname, str(episode_rewards[algorithm]))

    # start shutdown process and wait for finish
    pool.close()
    pool.join()