import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci


# TODO
# Add option for more simplified state, and more detailed state
# - add option to display full state with distinction between cars and bicycles, and direction of pedestrians crossing


def _discretize(xs: list[int], thresholds: tuple[int] = (0, 2, 5)) -> list[int]:
    # discretize value to a value between 0-3
    ys = [-1] * len(xs)
    for i, x in enumerate(xs):
        if x <= thresholds[0]:
            ys[i] = 0 # zero
        elif x <= thresholds[1]:
            ys[i] = 1 # low
        elif x <= thresholds[2]:
            ys[i] = 2 # moderate
        else:
            ys[i] = 3 # high
    return ys


def get_current_tls_phase(tls_id: str) -> str:
    # get the current phase of the default traffic light system (8 phases => 3-3-2)
    return traci.trafficlight.getPhase(tls_id)


def _get_waiting_vehicles(detector_id: str) -> int:
    # get number of cars/bicycles (up to detector limit) waiting in the lane
    return traci.lanearea.getLastStepVehicleNumber(detector_id)


def get_all_waiting_vehicles(detectors: list[list[str]]) -> list[int]:
    # return the number of waiting vehicles in the specified detectors
    waiting_vehicles = []
    for detector_group in detectors:
        count = 0
        for detector in detector_group:
            count += _get_waiting_vehicles(detector)
        waiting_vehicles.append(count)
    return waiting_vehicles


def _get_waiting_peds(crossing_id: str, waiting_edge_ids: tuple[str, str]) -> int:
    # get number of pedestrians waiting to use a crossing 
    possible_peds = traci.edge.getLastStepPersonIDs(waiting_edge_ids[0]) + traci.edge.getLastStepPersonIDs(waiting_edge_ids[1])
    count = 0
    for ped in possible_peds:
        if traci.person.getNextEdge(ped) == crossing_id:
            count += 1
    return count


def get_all_waiting_peds(crossings: list[tuple[str, str, str]]) -> list[int]:
    # return the number of waiting pedestrians at the specified crossings
    waiting_peds = []
    for crossing in crossings:
        count = _get_waiting_peds(crossing[0], crossing[1:])
        waiting_peds.append(count)
    return waiting_peds


def get_state(tls: str, detectors: list[list[str]], crossings: list[tuple[str, str, str]]) -> tuple[int, ...]:
    # get current phase of traffic light system
    tls_phase = get_current_tls_phase(tls)

    # get number of vehicles waiting in each queue
    waiting_vehicles = get_all_waiting_vehicles(detectors)

    # get number of pedestrians waiting to use each crossing
    waiting_peds = get_all_waiting_peds(crossings)

    # simplify state
    # combine 4 pedestrian areas into one, combine north and south bound, combine west and east bound
    waiting_peds = [sum(waiting_peds)]
    waiting_vehicles = [waiting_vehicles[0] + waiting_vehicles[2], waiting_vehicles[1] + waiting_vehicles[3]]

    # discretize to limit number of distinct values/combinations
    waiting_vehicles = _discretize(waiting_vehicles)
    waiting_peds = _discretize(waiting_peds)

    return (tls_phase, ) + tuple(waiting_vehicles) + tuple(waiting_peds)