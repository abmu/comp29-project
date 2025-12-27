from .settings import STEP_LENGTH, TOTAL_STEPS
from .utils import ceil
from .state import get_current_tls_phase, get_all_waiting_vehicles, get_all_waiting_peds, get_vehicle_throughput, get_peds_throughput
from .reward import get_reward


# for reference, the 8 traffic light phases defined in 'demo/main.net.xml'
tls_logic = """
<tlLogic id="CJ_1" type="static" programID="0" offset="0">
    <phase duration="30" state="GGgGGgrrrrGGgGGgrrrrrrrr"/>
    <phase duration="3"  state="yyyyyyrrrryyyyyyrrrrrrrr"/>
    <phase duration="2"  state="rrrrrrrrrrrrrrrrrrrrrrrr"/>
    <phase duration="30" state="rrrrrrGGggrrrrrrGGggrrrr"/>
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


def _steps_to_duration(steps: int) -> float:
    # convert number of steps to duration in the simulation
    return steps * STEP_LENGTH


def _step(conn, tls_id: str, stats_mode: bool) -> float:
    # perform a single step and return the reward
    conn.simulationStep()
    if len(conn.simulation.getStartingTeleportIDList()):
        raise RuntimeError('Teleport detected!')
    
    return get_reward(get_all_waiting_vehicles(conn, tls_id), get_all_waiting_peds(conn, tls_id), get_vehicle_throughput(conn, tls_id), get_peds_throughput(conn, tls_id), stats_mode=stats_mode)


def _run_action(conn, tls_id: str, curr_step: int, action: int, duration: int, curr_reward: int, stats_mode: bool) -> tuple[int, float]:
    # peform action changing phase on the traffic light system, and return updated step number and cumulative reward
    if curr_step >= TOTAL_STEPS:
        return curr_step, curr_reward

    conn.trafficlight.setPhase(tls_id, action)
    conn.trafficlight.setPhaseDuration(tls_id, duration)
    
    # execute simulation steps, ensuring total permitted steps is not exceeded
    steps = _duration_to_steps(duration)
    for i in range(steps):
        if curr_step < TOTAL_STEPS:
            curr_reward += _step(conn, tls_id, stats_mode)
            curr_step += 1
        else:
            break
    
    return curr_step, curr_reward


def perform_action(conn, tls_id: str, curr_step: int, action: int | None, stats_mode: bool = False) -> tuple[int, float, float]:
    # perform specified action, ensuring that the phase switch is also run if action is different to current phase
    start_step = curr_step
    curr_reward = 0
    if action is None:
        if curr_step < TOTAL_STEPS:
            curr_reward += _step(conn, tls_id, stats_mode)
            curr_step += 1
    else:
        tls_phase = get_current_tls_phase(conn, tls_id)
        if action != tls_phase:
            phase_switch = ACTION_SPACE[tls_phase]['phase_switch']
            for act, dur in phase_switch:
                curr_step, curr_reward = _run_action(conn, tls_id, curr_step, act, dur, curr_reward, stats_mode=stats_mode)

        duration = ACTION_SPACE[action]['duration']
        curr_step, curr_reward = _run_action(conn, tls_id, curr_step, action, duration, curr_reward, stats_mode=stats_mode)

    return curr_step, curr_reward, _steps_to_duration(curr_step - start_step)
