# SUMO simulation settings
GUI = False
SIMULATION_TIME = 3600
STEP_LENGTH = 0.10 * 10
TOTAL_STEPS = int(SIMULATION_TIME / STEP_LENGTH)

DIR_PREFIX = '../simulation/'
NET_NAME = 'demo'

SUMO_CONFIG = ['sumo-gui'] if GUI else ['sumo']
SUMO_CONFIG += [
    '-c', f'{DIR_PREFIX}simulation.sumocfg',
    '--step-length', str(STEP_LENGTH),
    '--lateral-resolution', '0',
    '--net-file', f'{DIR_PREFIX}networks/{NET_NAME}/main.net.xml',
    '--route-files', f'{DIR_PREFIX}routes/{NET_NAME}/bicycle.rou.xml,{DIR_PREFIX}routes/{NET_NAME}/car.rou.xml,{DIR_PREFIX}routes/{NET_NAME}/pedestrian.rou.xml',
    '--additional-files', f'{DIR_PREFIX}networks/{NET_NAME}/detectors.add.xml'
    # '--statistic-output', '../simulation/statistics.xml',
    # '--tripinfo-output.write-unfinished',
    # '--duration-log.statistics',
    # '--no-warnings',
    # '--no-step-log',
]

# ID of the traffic light system
tls_id = 'CJ_1'

# IDs of the lane detectors/cameras
queue_ids = [
    [f'{tls_id}_NB_1_1', f'{tls_id}_NB_1_2'],
    [f'{tls_id}_WB_1_1'],
    [f'{tls_id}_SB_1_1', f'{tls_id}_SB_1_2'],
    [f'{tls_id}_EB_1_1'],
]

# IDs of crossings and the corresponding walking areas
crossing_ids = [
    (f':{tls_id}_c0', f':{tls_id}_w0', f':{tls_id}_w1'),
    (f':{tls_id}_c1', f':{tls_id}_w1', f':{tls_id}_w2'),
    (f':{tls_id}_c2', f':{tls_id}_w2', f':{tls_id}_w3'),
    (f':{tls_id}_c3', f':{tls_id}_w3', f':{tls_id}_w0'),
]

# IDs of induction loops used to detect throughput
induction_ids = [
    [f'{tls_id}_NB_2_1', f'{tls_id}_NB_2_2'],
    [f'{tls_id}_WB_2_1', f'{tls_id}_WB_2_2'],
    [f'{tls_id}_SB_2_1', f'{tls_id}_SB_2_2'],
    [f'{tls_id}_EB_2_1', f'{tls_id}_EB_2_2'],
]