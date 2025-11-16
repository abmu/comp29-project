import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

from settings import SUMO_CONFIG, TOTAL_STEPS, tls_id, detector_ids, crossing_ids
from state import get_state, get_all_waiting_vehicles, get_all_waiting_peds
from action import ACTION_SPACE, perform_action
from reward import get_reward


traci.start(SUMO_CONFIG)

total_reward = 0

action_loop = [0,0,0,3,3,3,6]
curr_idx = 0

step = 0
while step < TOTAL_STEPS:
    action = action_loop[curr_idx]
    curr_idx = (curr_idx + 1) % len(action_loop)

    step = perform_action(tls_id, step, TOTAL_STEPS, action)

    state = get_state(tls_id, detector_ids, crossing_ids)
    reward = get_reward(get_all_waiting_vehicles(detector_ids), get_all_waiting_peds(crossing_ids))
    total_reward += reward

    print(f'Step: {step}, State: {state}, Reward: {reward}')

print(f'Total Reward: {total_reward}')

traci.close()