import random
import multiprocessing as mp
from pathlib import Path
from environment import get_sumo_cfg, set_route, StateBus
from agent import DefaultRunner
from fixed_timer import FixedTimer
from q_learning import QLearning
from deep_q_learning import DeepQLearning
from comm_deep_q_learning import CommunicativeDeepQLearning
from network import Network
from utils import file_dump


SEED = 29  # may not work well with multiple parallel processes -- non-determinism of execution

DIR_PREFIX = '../simulation/'

NET_NAME = 'demo'  # this 'NET' refers to the SUMO network definition!
MODE = 'train'  # 'train' or 'eval'

RESULTS_DIR = f'results/{NET_NAME}/'


def _make_comm_network(tls_ids: list[str], save_dir: str, train_mode: bool, compression_level: int, sumo_cfg: list[str]) -> Network:
    state_bus = StateBus()

    agents = [
        CommunicativeDeepQLearning(
            tls_id=tls_id,
            save_dir=save_dir,
            train_mode=train_mode,
            state_bus=state_bus,
            compression_level=compression_level
        )
        for tls_id in tls_ids
    ]

    return Network(agents=agents, sumo_cfg=sumo_cfg)    


NETWORKS = {
    # Get cache stats used to calculate reward weights
    # 'ft': Network(
    #     agents=[
    #         FixedTimer(
    #             tls_id='CJ_1',  # traffic light system ID
    #             save_dir=RESULTS_DIR,
    #             stats_mode=True
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    # ),



    'ft': Network(
        agents=[
            FixedTimer(
                tls_id='CJ_1',
                save_dir=RESULTS_DIR,
                stats_mode=False
            )
        ],
        sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    ),
    'ql_c0': Network(
        agents=[
            QLearning(
                tls_id='CJ_1',
                save_dir=RESULTS_DIR,
                train_mode=(MODE == 'train'),
                compression_level=0
            )
        ],
        sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    ),
    'ql_c1': Network(
        agents=[
            QLearning(
                tls_id='CJ_1',
                save_dir=RESULTS_DIR,
                train_mode=(MODE == 'train'),
                compression_level=1
            )
        ],
        sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    ),
    'ql_c2': Network(
        agents=[
            QLearning(
                tls_id='CJ_1',
                save_dir=RESULTS_DIR,
                train_mode=(MODE == 'train'),
                compression_level=2
            )
        ],
        sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    ),
    'dqn_c0': Network(
        agents=[
            DeepQLearning(
                tls_id='CJ_1',
                save_dir=RESULTS_DIR,
                train_mode=(MODE == 'train'),
                compression_level=0
            )
        ],
        sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    ),
    'dqn_c1': Network(
        agents=[
            DeepQLearning(
                tls_id='CJ_1',
                save_dir=RESULTS_DIR,
                train_mode=(MODE == 'train'),
                compression_level=1
            )
        ],
        sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    ),
    'dqn_c2': Network(
        agents=[
            DeepQLearning(
                tls_id='CJ_1',
                save_dir=RESULTS_DIR,
                train_mode=(MODE == 'train'),
                compression_level=2
            )
        ],
        sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    ),



    # 'zebra': Network(
    #     agents=[
    #         DefaultRunner(
    #             tls_id='CJ_2',
    #             save_dir=RESULTS_DIR,
    #             stats_mode=False
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME, netfile='main')
    # ),
    # 'fixed_timer': Network(
    #     agents=[
    #         FixedTimer(
    #             tls_id='CJ_2',
    #             save_dir=RESULTS_DIR,
    #             stats_mode=False
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME, netfile='tls')
    # ),
    # 'q_learning': Network(
    #     agents=[
    #         QLearning(
    #             tls_id='CJ_2',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=True
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME, netfile='tls')
    # ),
    # 'deep_q_learning': Network(
    #     agents=[
    #         DeepQLearning(
    #             tls_id='CJ_2',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=True
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME, netfile='tls')
    # ),
    # 'deep_q_learning_uncompressed': Network(
    #     agents=[
    #         DeepQLearning(
    #             tls_id='CJ_2',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=False
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME, netfile='tls')
    # ),



    # 'fixed_timer': Network(
    #     agents=[
    #         FixedTimer(
    #             tls_id='CJ_1',
    #             save_dir=RESULTS_DIR,
    #             stats_mode=False
    #         ),
    #         FixedTimer(
    #             tls_id='CJ_2',
    #             save_dir=RESULTS_DIR,
    #             stats_mode=False
    #         ),
    #         FixedTimer(
    #             tls_id='CJ_9',
    #             save_dir=RESULTS_DIR,
    #             stats_mode=False
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    # ),
    # 'q_learning': Network(
    #     agents=[
    #         QLearning(
    #             tls_id='CJ_1',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=True
    #         ),
    #         QLearning(
    #             tls_id='CJ_2',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=True
    #         ),
    #         QLearning(
    #             tls_id='CJ_9',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=True
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    # ),
    # 'deep_q_learning': Network(
    #     agents=[
    #         DeepQLearning(
    #             tls_id='CJ_1',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=True
    #         ),
    #         DeepQLearning(
    #             tls_id='CJ_2',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=True
    #         ),
    #         DeepQLearning(
    #             tls_id='CJ_9',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=True
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    # ),
    # 'deep_q_learning_uncompressed': Network(
    #     agents=[
    #         DeepQLearning(
    #             tls_id='CJ_1',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=False
    #         ),
    #         DeepQLearning(
    #             tls_id='CJ_2',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=False
    #         ),
    #         DeepQLearning(
    #             tls_id='CJ_9',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=False
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    # ),
    # 'deep_q_learning_communicative': _make_comm_network(
    #     tls_ids=[
    #         'CJ_1',
    #         'CJ_2',
    #         'CJ_9'
    #     ],
    #     save_dir=RESULTS_DIR,
    #     train_mode=(MODE == 'train'),
    #     compression_level=True,
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    # ),
    # 'deep_q_learning_communicative_uncompressed': _make_comm_network(
    #     tls_ids=[
    #         'CJ_1',
    #         'CJ_2',
    #         'CJ_9'
    #     ],
    #     save_dir=RESULTS_DIR,
    #     train_mode=(MODE == 'train'),
    #     compression_level=False,
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    # ),
}


def run_ep(args: tuple[str, int]) -> tuple[str, float]:
    """
    Run an episode using the specified algorithm
    """
    net, epoch = args
    try:
        reward = NETWORKS[net].run(epoch)
        return net, reward
    except Exception as e:
        print(f'[{net}] [{epoch}] exception: {e}')
        return net, None


if __name__ == "__main__":
    random.seed(SEED)

    episode_rewards = {a: [] for a in NETWORKS}
    
    # create a process pool
    pool = mp.Pool(processes=len(NETWORKS))

    routes_dir = Path(f'{DIR_PREFIX}routes/{NET_NAME}/{MODE}/').glob('*')
    count = sum(1 if f.is_dir() else 0 for f in routes_dir)  # count the number of folders in the routes directory
    print(f'Using {count} "{MODE}" routes for the network "{NET_NAME}"...')

    for episode in range(1, count+1):
        print(f'\n=== Episode: {episode} ===')
        
        # set SUMO route
        set_route(episode, dirprefix=DIR_PREFIX, netname=NET_NAME, mode=MODE)

        # run NETWORKS in parallel
        print(f'Running {len(NETWORKS)} instances of SUMO...')
        jobs = [(network, episode) for network in NETWORKS]
        results = pool.map(run_ep, jobs)

        for network, reward in results:
            print(f'[{network}] reward = {reward}')

            episode_rewards[network].append(reward)

            # save to file
            fname = f'{RESULTS_DIR}{MODE}/{network}.txt'
            file_dump(fname, str(episode_rewards[network]))

    # start shutdown process and wait for finish
    pool.close()
    pool.join()