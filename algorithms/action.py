import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci


def perform_action(tls_id: str, action: int) -> None:
    # 8 traffic light phases defined in 'main.net.xml'
    # index 2, 5, and 7 are identical (all red lights)
    traci.trafficlight.setPhase(tls_id, action)