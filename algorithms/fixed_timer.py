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

# IDs of the traffic light system and lane detectors/cameras
tls_id = 'CJ_1'
detector_ids = [
    'CJ_1_SB_1',
    'CJ_1_SB_2',
    'CJ_1_NB_1',
    'CJ_1_NB_2',
    'CJ_1_EB_1',
    'CJ_1_WB_1',
]


# Get number of pedestrians - useful link that could help https://sumo.dlr.de/docs/Tutorials/TraCIPedCrossing.html
def get_peds():
    ...


def get_current_tls_phase(tls_id: str) -> str:
    return traci.trafficlight.getPhase(tls_id)


def get_detector_queue_length(detector_id: str) -> int:
    return traci.lanearea.getLastStepVehicleNumber(detector_id)


def get_state(tls: str, *args: str) -> tuple[str, ...]:
    # get current phase of traffic light system
    tls_phase = get_current_tls_phase(tls)

    queue_lengths = []
    for detector in args:
        size = get_detector_queue_length(detector)
        queue_lengths.append(size)

    return (tls_phase, ) + tuple(queue_lengths)


traci.start(sumo_config)

for step in range(TOTAL_STEPS):
    traci.simulationStep()
    state = get_state(tls_id, *detector_ids)
    print(f'Step: {step}, State: {state}')

traci.close()