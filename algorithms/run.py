import time
import traceback
from multiprocessing import Process, Queue, Barrier
from datetime import timedelta
from pathlib import Path
from environment import get_sumo_cfg, set_route, StateBus
from agent import DefaultRunner
from fixed_timer import FixedTimer
from q_learning import QLearning
from deep_q_learning import DeepQLearning
from comm_deep_q_learning import CommunicativeDeepQLearning
from network import Network
from utils import file_dump


DIR_PREFIX = '../simulation/'

NET_NAME = 'crossing'  # this 'NET' refers to the SUMO network definition!
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



    # 'ft': Network(
    #     agents=[
    #         FixedTimer(
    #             tls_id='CJ_1',
    #             save_dir=RESULTS_DIR,
    #             stats_mode=False
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    # ),
    # 'ql_c0': Network(
    #     agents=[
    #         QLearning(
    #             tls_id='CJ_1',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=0
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    # ),
    # 'ql_c1': Network(
    #     agents=[
    #         QLearning(
    #             tls_id='CJ_1',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=1
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    # ),
    # 'ql_c2': Network(
    #     agents=[
    #         QLearning(
    #             tls_id='CJ_1',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=2
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    # ),
    # 'dqn_c0': Network(
    #     agents=[
    #         DeepQLearning(
    #             tls_id='CJ_1',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=0
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    # ),
    # 'dqn_c1': Network(
    #     agents=[
    #         DeepQLearning(
    #             tls_id='CJ_1',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=1
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    # ),
    # 'dqn_c2': Network(
    #     agents=[
    #         DeepQLearning(
    #             tls_id='CJ_1',
    #             save_dir=RESULTS_DIR,
    #             train_mode=(MODE == 'train'),
    #             compression_level=2
    #         )
    #     ],
    #     sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME)
    # ),



    'zebra': Network(
        agents=[
            DefaultRunner(
                tls_id='CJ_2',
                save_dir=RESULTS_DIR,
                stats_mode=False
            )
        ],
        sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME, netfile='main')
    ),
    'ft': Network(
        agents=[
            FixedTimer(
                tls_id='CJ_2',
                save_dir=RESULTS_DIR,
                stats_mode=False
            )
        ],
        sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME, netfile='tls')
    ),
    'ql_c2': Network(
        agents=[
            QLearning(
                tls_id='CJ_2',
                save_dir=RESULTS_DIR,
                train_mode=(MODE == 'train'),
                compression_level=2
            )
        ],
        sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME, netfile='tls')
    ),
    'dqn_c0': Network(
        agents=[
            DeepQLearning(
                tls_id='CJ_2',
                save_dir=RESULTS_DIR,
                train_mode=(MODE == 'train'),
                compression_level=0
            )
        ],
        sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME, netfile='tls')
    ),
    'dqn_c1': Network(
        agents=[
            DeepQLearning(
                tls_id='CJ_2',
                save_dir=RESULTS_DIR,
                train_mode=(MODE == 'train'),
                compression_level=1
            )
        ],
        sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME, netfile='tls')
    ),
    'dqn_c2': Network(
        agents=[
            DeepQLearning(
                tls_id='CJ_2',
                save_dir=RESULTS_DIR,
                train_mode=(MODE == 'train'),
                compression_level=2
            )
        ],
        sumo_cfg=get_sumo_cfg(DIR_PREFIX, NET_NAME, netfile='tls')
    ),



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
    # 'cdqn_c0': _make_comm_network(
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
    # 'cdqn_c1': _make_comm_network(
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


def network_worker(net: str, task_q: Queue, result_q: Queue, barrier: Barrier) -> None:
    """
    Run a persistent process per network
    """
    network = NETWORKS[net]

    while True:
        msg = task_q.get()
        if msg == 'STOP':
            break
        episode = msg
        try:
            reward = network.run(episode)
            result_q.put((net, episode, reward))
        except Exception as e:
            traceback.print_exc()
            result_q.put((net, episode, None))

        # wait at barrier before getting next task
        barrier.wait()


if __name__ == "__main__":
    episode_rewards = {a: [] for a in NETWORKS}

    # setup multiprocessing workers
    task_q = Queue()
    result_q = Queue()
    num_workers  = len(NETWORKS)
    barrier = Barrier(num_workers)
    workers = []
    for network in NETWORKS:
        p = Process(
            target=network_worker,
            args=(network, task_q, result_q, barrier),
            daemon=True
        )
        p.start()
        workers.append(p)
    print(f'Running {len(NETWORKS)} workers')
    
    routes_dir = Path(f'{DIR_PREFIX}routes/{NET_NAME}/{MODE}/').glob('*')
    count = sum(1 if f.is_dir() else 0 for f in routes_dir)  # count the number of folders in the routes directory
    print(f'Using {count} "{MODE}" routes for the network "{NET_NAME}"...')

    start_time = time.time()

    for episode in range(1, count+1):
        print(f'\n=== Episode: {episode} ===')
        
        # set SUMO route
        set_route(episode, dirprefix=DIR_PREFIX, netname=NET_NAME, mode=MODE)

        for _ in workers:
            task_q.put(episode)

        for _ in workers:
            network, ep, reward = result_q.get()
            print(f'[{network}] reward = {reward}')

            episode_rewards[network].append(reward)

            # save to file
            fname = f'{RESULTS_DIR}{MODE}/{network}.txt'
            file_dump(fname, str(episode_rewards[network]))

    end_time = time.time()
    time_elapsed = timedelta(seconds=(end_time-start_time))

    print(f'\nTotal time taken: {time_elapsed}')
    file_dump(f'{RESULTS_DIR}{MODE}/time.txt', str(time_elapsed))

    for _ in workers:
        task_q.put('STOP')

    for p in workers:
        p.join()
