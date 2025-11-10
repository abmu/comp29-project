import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci


# 8 traffic light phases defined in 'main.net.xml'
tls_logic = """
<tlLogic id="CJ_1" type="static" programID="0" offset="0">
    <phase duration="30" state="gGggGgrrrrgGggGgrrrrrrrr"/>
    <phase duration="3"  state="yyyyyyrrrryyyyyyrrrrrrrr"/>
    <phase duration="2"  state="rrrrrrrrrrrrrrrrrrrrrrrr"/>
    <phase duration="30" state="rrrrrrgGggrrrrrrgGggrrrr"/>
    <phase duration="3"  state="rrrrrryyyyrrrrrryyyyrrrr"/>
    <phase duration="2"  state="rrrrrrrrrrrrrrrrrrrrrrrr"/>
    <phase duration="10" state="rrrrrrrrrrrrrrrrrrrrGGGG"/>
    <phase duration="10" state="rrrrrrrrrrrrrrrrrrrrrrrr"/>
</tlLogic>
"""

# only phase index 0, 3, and 6 are available actions
#
# graceful switch defines the phases that should be run when switching away from that action
# list[(phase index, duration), ...]
ACTION_SPACE = {
    # north bound and south bound
    0: {
        'min_duration': 10,
        'graceful_switch': [(1,3),(2,2)]
    },
    # east bound and west bound
    3: {
        'min_duration': 10,
        'graceful_switch': [(4,3),(5,2)]
    },
    # pedestrians
    6: {
        'min_duration': 10,
        'graceful_switch': [(7,10)]
    }
}


def perform_action(tls_id: str, prev_action: int | None, action: int) -> int:
    # peform action changing phase on the traffic light system, and return total duration
    traci.trafficlight.setPhase(tls_id, action)
    duration = 
    traci.trafficlight.setPhaseDuration(tls_id, duration)