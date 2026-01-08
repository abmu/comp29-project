# SUMO simulation settings
GUI = False
SIMULATION_TIME = 3600
STEP_LENGTH = 0.10 * 10
TOTAL_STEPS = int(SIMULATION_TIME / STEP_LENGTH)

TLS_IDS = {
    # ID of the traffic light system
    'CJ_1': {
        # IDs of the lane detectors/cameras
        'queues': [
            # MUST FOLLOW PARTICULAR ORDER -- North Bound, West Bound, South Bound, East Bound
            ['CJ_1_NB_1_1', 'CJ_1_NB_1_2'],
            ['CJ_1_WB_1_1'],
            ['CJ_1_SB_1_1', 'CJ_1_SB_1_2'],
            ['CJ_1_EB_1_1'],
        ],
        # IDs of crossings and the corresponding walking areas
        'crossings': [
            (':CJ_1_c0', ':CJ_1_w0', ':CJ_1_w1'),
            (':CJ_1_c1', ':CJ_1_w1', ':CJ_1_w2'),
            (':CJ_1_c2', ':CJ_1_w2', ':CJ_1_w3'),
            (':CJ_1_c3', ':CJ_1_w3', ':CJ_1_w0'),
        ],
        # IDs of induction loops used to detect throughput
        'inductions': [
            ['CJ_1_NB_2_1', 'CJ_1_NB_2_2'],
            ['CJ_1_WB_2_1', 'CJ_1_WB_2_2'],
            ['CJ_1_SB_2_1', 'CJ_1_SB_2_2'],
            ['CJ_1_EB_2_1', 'CJ_1_EB_2_2'],
        ]
    },
    'CJ_2': {
        'queues': [
            ['CJ_2_NB_1_1'],
            ['CJ_2_WB_1_1'],
            [],
            ['CJ_2_EB_1_1', 'CJ_2_EB_1_2'],
        ],
        'crossings': [
            (':CJ_2_c0', ':CJ_2_w0', ':CJ_2_w1'),
            (':CJ_2_c1', ':CJ_2_w1', ':CJ_2_w2'),
        ],
        'inductions': [
            [],
            ['CJ_2_WB_2_1'],
            ['CJ_2_SB_1_1'],
            ['CJ_2_EB_2_1', 'CJ_2_EB_2_2'],
        ]
    },
}


def get_sumo_cfg(dirprefix: str, netname: str, netfile: str = 'main') -> list[str]:
    sumo_cfg = ['sumo-gui'] if GUI else ['sumo']
    sumo_cfg += [
        '-c', f'{dirprefix}simulation.sumocfg',
        '--step-length', str(STEP_LENGTH),
        '--lateral-resolution', '0',
        '--net-file', f'{dirprefix}networks/{netname}/{netfile}.net.xml',
        '--route-files', f'{dirprefix}routes/{netname}/bicycle.rou.xml,{dirprefix}routes/{netname}/car.rou.xml,{dirprefix}routes/{netname}/pedestrian.rou.xml',
        '--additional-files', f'{dirprefix}networks/{netname}/detectors.add.xml',
        '--no-warnings',
        # '--no-step-log',
        # '--statistic-output', '../simulation/statistics.xml',
        # '--tripinfo-output.write-unfinished',
        # '--duration-log.statistics',
    ]
    return sumo_cfg