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
# IDs of crossings and the corresponding walking areas
crossing_ids = [
    (':CJ_1_c0', ':CJ_1_w0', ':CJ_1_w1'),
    (':CJ_1_c1', ':CJ_1_w1', ':CJ_1_w2'),
    (':CJ_1_c2', ':CJ_1_w2', ':CJ_1_w3'),
    (':CJ_1_c3', ':CJ_1_w3', ':CJ_1_w0'),
]


def get_peds(crossing_id: str, waiting_edge_ids: tuple[str, str]) -> int:
    # get number of pedestrians waiting to use a crossing 
    peds = traci.edge.getLastStepPersonIDs(waiting_edge_ids[0]) + traci.edge.getLastStepPersonIDs(waiting_edge_ids[1])
    count = 0
    for ped in peds:
        if traci.person.getNextEdge(ped) == crossing_id:
            count += 1
    return count

def get_current_tls_phase(tls_id: str) -> str:
    return traci.trafficlight.getPhase(tls_id)


def get_detector_queue_length(detector_id: str) -> int:
    return traci.lanearea.getLastStepVehicleNumber(detector_id)


def get_state(tls: str, detectors: list[str], crossings: list[tuple[str]]) -> tuple[str, ...]:
    # get current phase of traffic light system
    tls_phase = get_current_tls_phase(tls)

    # get number of vehicles waiting in each queue
    queue_lengths = []
    for detector in detectors:
        size = get_detector_queue_length(detector)
        queue_lengths.append(size)

    # get number of pedestrians waiting to use each crossing
    num_peds = []
    for crossing in crossings:
        count = get_peds(crossing[0], crossing[1:])
        num_peds.append(count)

    return (tls_phase, ) + tuple(queue_lengths) + tuple(num_peds)


traci.start(sumo_config)

for step in range(TOTAL_STEPS):
    traci.simulationStep()
    state = get_state(tls_id, detector_ids, crossing_ids)
    print(f'Step: {step}, State: {state}')

traci.close()