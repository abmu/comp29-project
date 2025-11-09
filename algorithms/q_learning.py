import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

from settings import SUMO_CONFIG, TOTAL_STEPS, tls_id, detector_ids, crossing_ids
from state import get_state, get_current_tls_phase, get_all_waiting_vehicles, get_all_waiting_peds
from action import perform_action
from reward import get_reward

... FIX POISSION RANDOM TRIP GENERATION!


traci.start(SUMO_CONFIG)

total_reward = 0

for step in range(TOTAL_STEPS):
    traci.simulationStep()
    
    state = get_state(tls_id, detector_ids, crossing_ids)
    reward = get_reward(get_all_waiting_vehicles(detector_ids), get_all_waiting_peds(crossing_ids))
    total_reward += reward

    print(f'Step: {step}, State: {state}, Reward: {reward}')

traci.close()