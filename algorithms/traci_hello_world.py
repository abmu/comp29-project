import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

sumo_config = [
    'sumo-gui',
    '-c', '../simulation/simulation.sumocfg',
]

traci.start(sumo_config)

TOTAL_STEPS = 10000

for step in range(TOTAL_STEPS):
    traci.simulationStep()

traci.close()