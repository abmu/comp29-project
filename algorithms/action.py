import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci

from settings import STEP_LENGTH
from utils import ceil


# for reference, the 8 traffic light phases defined in 'main.net.xml'
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

# define the traffic light phase indexes which are available as actions
# 'phase_switch' defines the sequence of phases that should be run when switching away from that action
# list[(phase index, duration), ...]
ACTION_SPACE = {
    # north and south bound
    0: {
        'duration': 10,
        'phase_switch': [(1,3),(2,2)]
    },
    # east and west bound
    3: {
        'duration': 10,
        'phase_switch': [(4,3),(5,2)]
    },
    # pedestrians
    6: {
        'duration': 10,
        'phase_switch': [(7,10)]
    }
}


def _duration_to_steps(duration: int) -> int:
    # convert duration to number of steps in the simulation
    return ceil(duration / STEP_LENGTH)


def _run_action(tls_id: str, curr_step: int, total_steps: int, action: int, duration: int) -> int:
    # peform action changing phase on the traffic light system, and return updated step number
    if curr_step >= total_steps:
        return curr_step

    traci.trafficlight.setPhase(tls_id, action)
    traci.trafficlight.setPhaseDuration(tls_id, duration)
    
    # execute simulation steps, ensuring total permitted steps is not exceeded
    steps = _duration_to_steps(duration)
    for i in range(steps):
        if curr_step < total_steps:
            traci.simulationStep()
            curr_step += 1
        else:
            break
    
    return curr_step

def perform_action(tls_id: str, curr_step: int, total_steps: int, action: int, prev_action: int | None = None) -> int:
    # perform specified action, ensuring that the phase switch is also run if action and previous_action are different
    if prev_action != None and prev_action != action:
        phase_switch = ACTION_SPACE[prev_action]['phase_switch']
        for act, dur in phase_switch:
            curr_step = _run_action(tls_id, curr_step, total_steps, act, dur)

    duration = ACTION_SPACE[action]['duration']
    curr_step = _run_action(tls_id, curr_step, total_steps, action, duration)

    return curr_step
