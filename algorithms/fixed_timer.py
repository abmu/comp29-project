import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

from settings import SUMO_CONFIG, TOTAL_STEPS, tls_id, queue_ids, crossing_ids
from utils import file_dump
from routes import set_route
from state import get_state
from action import perform_action


RESULTS_FILE = 'results/fixed_timer.txt'


ACTION_LOOP = [0,0,0,3,3,3,6]

EPISODES = 1000

episode_rewards = []

for episode in range(EPISODES):

    print(f'Episode: {episode + 1}')

    # set SUMO route
    set_route(episode+1)

    print(f'Running SUMO...')

    # run fixed timer algorithm
    total_reward = 0
    curr_idx = 0
    step = 0
    traci.start(SUMO_CONFIG)

    while step < TOTAL_STEPS:
        state = get_state(tls_id, queue_ids, crossing_ids)
        action = ACTION_LOOP[curr_idx]

        step, reward, _ = perform_action(tls_id, step, TOTAL_STEPS, action)

        curr_idx = (curr_idx + 1) % len(ACTION_LOOP)
        total_reward += reward

        # print(f'Step: {step}, State: {state}, Action: {action}, Reward: {reward}')

    traci.close()

    episode_rewards.append(total_reward)

    print(f'Total Reward: {total_reward}\n')
    file_dump(RESULTS_FILE, str(episode_rewards))