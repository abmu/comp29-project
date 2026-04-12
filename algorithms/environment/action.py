from .settings import STEP_LENGTH
from .utils import ceil
from .state import get_current_tls_phase, get_all_waiting_vehicles, get_all_waiting_peds, get_vehicle_throughput, get_peds_throughput
from .reward import PENALTY, get_reward


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


def simulation_step(conn) -> float:
    # perform a single step
    conn.simulationStep()


class Controller:
    def __init__(self, conn, tls_id: str, stats_mode: bool = False, offset: float = 0) -> None:
        self.conn = conn
        self.tls_id = tls_id
        self.stats_mode = stats_mode
        self.initialised = False
        self.curr_action = None
        self.curr_dur = None
        self.next = []
        self.total_steps = 0
        if self.tls_id not in self.conn.trafficlight.getIDList():
            # not a traffic light
            self._controlled_lanes = set()
        else:
            self._controlled_lanes = set(self.conn.trafficlight.getControlledLanes(self.tls_id))
        self.set_offset(offset)

    def __str__(self) -> str:
        return f'Current action: {self.curr_action}\nDuration left (in steps): {self.curr_dur}\nNext actions: {self.next}\nSteps since last action set: {self.total_steps}\n'


    def finished(self) -> bool:
        # check if the current action (including phase switch) has completed
        return not self.curr_dur and not self.next


    def get_total_duration(self) -> int:
        # return the total duration of current action (including phase switch)
        return _steps_to_duration(self.total_steps)
    

    def _update_tls(self) -> None:
        # update the tls
        action, duration = self.next.pop(0)
        self.conn.trafficlight.setPhase(self.tls_id, action)
        self.conn.trafficlight.setPhaseDuration(self.tls_id, duration)

        self.curr_action = action
        self.curr_dur = _duration_to_steps(duration)


    def set_offset(self, offset_duration: float) -> None:
        self.offset = False
        if offset_duration:
            self.next = [(0, offset_duration)]  # set to phase 0 by default
            self.total_steps = 0
            self._update_tls()
            self.offset = True


    def set_action(self, new_action: int) -> None:
        # set new action
        self.next = []
        tls_phase = get_current_tls_phase(self.conn, self.tls_id)
        if new_action != tls_phase:
            self.next += ACTION_SPACE[tls_phase]['phase_switch']
        
        new_duration = ACTION_SPACE[new_action]['duration']
        self.next.append((new_action, new_duration))

        self.total_steps = 0
        self._update_tls()
        self.initialised = True    
    

    def _tls_teleport_penalty(self) -> float:
        # calculate the penalty for any teleports of entities going towards the TLS
        penalty = 0.0
        
        teleported = self.conn.simulation.getStartingTeleportIDList()
        for entity_id in teleported:
            lane_id = self.conn.person.getRoadID(entity_id) if entity_id in self.conn.person.getIDList() else self.conn.vehicle.getLaneID(entity_id)
            if lane_id in self._controlled_lanes:
                penalty += PENALTY
        
        return penalty
    

    def run(self, skip_reward=False) -> float:
        # run the controller and return the reward
        if self.offset:
            self.curr_dur -= 1
            if not self.curr_dur:
                self.offset = False
        else:
            if self.initialised and not self.finished():
                self.curr_dur -= 1
                self.total_steps += 1
    
                if not self.curr_dur and self.next:
                    self._update_tls()
        
        if skip_reward:
            return 0.0

        return get_reward(
            get_all_waiting_vehicles(self.conn, self.tls_id),
            get_all_waiting_peds(self.conn, self.tls_id),
            get_vehicle_throughput(self.conn, self.tls_id),
            get_peds_throughput(self.conn, self.tls_id),
            stats_mode=self.stats_mode
        ) + self._tls_teleport_penalty()
