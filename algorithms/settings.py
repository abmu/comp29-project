# SUMO simulation settings
SIMULATION_TIME = 3600
STEP_LENGTH = 0.10 * 10
TOTAL_STEPS = int(SIMULATION_TIME / STEP_LENGTH)
GUI_DELAY = 100

SEED = 29

SUMO_CONFIG = [
    # 'sumo-gui',
    # '--delay', str(GUI_DELAY),
    'sumo',
    '--no-warnings',
    '--duration-log.disable',
    '--no-step-log',
    '-c', '../simulation/simulation.sumocfg',
    '--step-length', str(STEP_LENGTH),
    '--lateral-resolution', '0'
]

# ID of the traffic light system
tls_id = 'CJ_1'

# IDs of the lane detectors/cameras
detector_ids = [
    [f'{tls_id}_NB_1', f'{tls_id}_NB_2'],
    [f'{tls_id}_WB_1'],
    [f'{tls_id}_SB_1', f'{tls_id}_SB_2'],
    [f'{tls_id}_EB_1'],
]

# IDs of crossings and the corresponding walking areas
crossing_ids = [
    (f':{tls_id}_c0', f':{tls_id}_w0', f':{tls_id}_w1'),
    (f':{tls_id}_c1', f':{tls_id}_w1', f':{tls_id}_w2'),
    (f':{tls_id}_c2', f':{tls_id}_w2', f':{tls_id}_w3'),
    (f':{tls_id}_c3', f':{tls_id}_w3', f':{tls_id}_w0'),
]