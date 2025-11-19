import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

import random
from settings import SUMO_CONFIG, TOTAL_STEPS, SEED, tls_id, detector_ids, crossing_ids
from utils import generate_routes, file_dump
from state import get_state, get_all_waiting_vehicles, get_all_waiting_peds
from action import perform_action
from reward import get_reward


ACTION_LOOP = [0,0,0,3,3,3,6]

EPISODES = 1000

episode_rewards = []

for episode in range(EPISODES):

    print(f'Episode: {episode + 1}')

    # generate a new route
    random.seed(SEED)
    # car_density = random.uniform(0.25, 2.0)
    # bicycle_density = random.uniform(0.5, 1.0)
    # pedestrian_density = random.uniform(0.5, 2.0)
    generate_routes(SEED)
    SEED += 1

    print(f'Running SUMO...')

    # run fixed timer algorithm
    total_reward = 0
    curr_idx = 0
    step = 0
    traci.start(SUMO_CONFIG)

    while step < TOTAL_STEPS:
        state = get_state(tls_id, detector_ids, crossing_ids)
        action = ACTION_LOOP[curr_idx]

        step = perform_action(tls_id, step, TOTAL_STEPS, action)

        curr_idx = (curr_idx + 1) % len(ACTION_LOOP)
        reward = get_reward(get_all_waiting_vehicles(detector_ids), get_all_waiting_peds(crossing_ids))
        total_reward += reward

        # print(f'Step: {step}, State: {state}, Action: {action}, Reward: {reward}')

    traci.close()

    episode_rewards.append(total_reward)

    print(f'Total Reward: {total_reward}\n')
    file_dump('./fixed_timer.txt', str(episode_rewards))