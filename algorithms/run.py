import random
import multiprocessing as mp
from environment import set_route
from fixed_timer import run as ft_run
from q_learning import run as q_run
from deep_q_learning import run as dqn_run
from utils import file_dump


SEED = 29

ALGORITHMS = {
    'fixed_timer': ft_run,
    'q_learning': q_run,
    'deep_q_learning': dqn_run
}

MODE = 'train'
TRAIN = 1000
EVAL = 5

TRAIN_DIR = 'results/train/'
EVAL_DIR = 'results/eval/'


def run_ep(args: tuple[str, int]) -> tuple[str, float]:
    """
    Run an episode using the specified algorithm
    """
    alg, epoch = args
    try:
        reward = ALGORITHMS[alg](epoch)
        return alg, reward
    except Exception as e:
        print(f'[{alg}] [{epoch}] exception: {e}')
        return alg, None


if __name__ == "__main__":
    random.seed(SEED)

    episode_rewards = {a: [] for a in ALGORITHMS}
    
    # create a process pool
    pool = mp.Pool(processes=len(ALGORITHMS))

    start, end = (1, TRAIN) if MODE == 'train' else (TRAIN+1, TRAIN+EVAL)
    results_dir = TRAIN_DIR if MODE == 'train' else EVAL_DIR
    print(f'Running on "{MODE}" routes...')

    for episode in range(start, end+1):
        print(f'\n=== Episode: {episode} ===')
        
        # set SUMO route
        set_route(episode)

        # run algorithms in parallel
        print(f'Running {len(ALGORITHMS)} instances of SUMO...')
        jobs = [(algorithm, episode) for algorithm in ALGORITHMS]
        results = pool.map(run_ep, jobs)

        for algorithm, reward in results:
            print(f'[{algorithm}] reward = {reward}')

            episode_rewards[algorithm].append(reward)

            # save to file
            fname = results_dir + algorithm + '.txt'
            file_dump(fname, str(episode_rewards[algorithm]))

    # start shutdown process and wait for finish
    pool.close()
    pool.join()