import random
import multiprocessing as mp
from environment import NET_NAME, set_route
from fixed_timer import FixedTimer
from q_learning import QLearning
from deep_q_learning import DeepQLearning
from utils import file_dump


SEED = 29

MODE = 'eval'
TRAIN = 1000
EVAL = 50

RESULTS_DIR = f'results/{NET_NAME}/'

ALGORITHMS = {
    'fixed_timer': FixedTimer(RESULTS_DIR, False),
    'q_learning': QLearning(RESULTS_DIR, False),
    'deep_q_learning': DeepQLearning(RESULTS_DIR, False)
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

    end = TRAIN if MODE == 'train' else EVAL
    print(f'Running on "{MODE}" routes...')

    for episode in range(1, end+1):
        print(f'\n=== Episode: {episode} ===')
        
        # set SUMO route
        set_route(episode, foldername=MODE)

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