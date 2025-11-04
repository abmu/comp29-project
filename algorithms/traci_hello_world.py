import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

SIMULATION_TIME = 3600
STEP_LENGTH = 0.10
TOTAL_STEPS = int(SIMULATION_TIME / STEP_LENGTH)

sumo_config = [
    'sumo-gui',
    '-c', '../simulation/simulation.sumocfg',
    '--step-length', str(STEP_LENGTH),
    '--delay', '100',
    '--lateral-resolution', '0'
]

traci.start(sumo_config)

for step in range(TOTAL_STEPS):
    traci.simulationStep()
    print(f'Step: {step}')

traci.close()