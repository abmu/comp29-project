import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

from settings import SUMO_CONFIG, TOTAL_STEPS, tls_id, detector_ids, crossing_ids
from state import get_state, get_all_waiting_vehicles, get_all_waiting_peds
from reward import get_reward


traci.start(SUMO_CONFIG)

for step in range(TOTAL_STEPS):
    traci.simulationStep()
    state = get_state(tls_id, detector_ids, crossing_ids)
    
    print(f'Step: {step}, State: {state}')

traci.close()