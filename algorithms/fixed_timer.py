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

action_loop = [0,0,0,3,3,3,6]
prev_idx = None
curr_idx = 0

step = 0
while step < TOTAL_STEPS:
    prev_action = action_loop[prev_idx] if prev_idx != None else None
    curr_action = action_loop[curr_idx]

    step = perform_action(tls_id, step, TOTAL_STEPS, curr_action, prev_action)

    prev_idx = curr_idx
    curr_idx = (curr_idx + 1) % len(action_loop)

    state = get_state(tls_id, detector_ids, crossing_ids)

    print(f'Step: {step}, State: {state}')

traci.close()