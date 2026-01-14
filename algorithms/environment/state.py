from enum import Enum
from .settings import TLS_IDS


class Compression(Enum):
    C0 = 0
    C1 = 1
    C2 = 2


def _to_compression_enum(value: str | Compression) -> Compression:
    # ensure value is a valid Compression enum
    if isinstance(value, Compression):
        return value
    return Compression(value)


def _discretize(xs: list[int], thresholds: tuple[int] = (0, 6, 12)) -> list[int]:
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


def get_current_tls_phase(conn, tls_id: str) -> str:
    # get the current phase of the default traffic light system (8 phases => 3-3-2)
    return conn.trafficlight.getPhase(tls_id)


def _get_waiting_vehicles(conn, detector_id: str) -> list[float]:
    # get time waiting of cars/bicycles (up to detector limit) waiting in the lane
    return [conn.vehicle.getWaitingTime(vehicle_id) for vehicle_id in conn.lanearea.getLastStepVehicleIDs(detector_id)]


def _get_vehicle_count(conn, detector_id: str) -> int:
    # get the number of vehicles crossing the detector
    return conn.inductionloop.getLastStepVehicleNumber(detector_id)


def get_all_waiting_vehicles(conn, tls: str) -> list[list[float]]:
    # return the waiting vehicles in the specified detectors
    detectors = TLS_IDS[tls]['queues']
    waiting_vehicles = []
    for detector_group in detectors:
        group = []
        for detector in detector_group:
            group.append(_get_waiting_vehicles(conn, detector))
        waiting_vehicles.append(group)
    return waiting_vehicles


def get_vehicle_throughput(conn, tls: str) -> int:
    # return the vehicle count that have crossed the induction loop detectors
    detectors = TLS_IDS[tls]['inductions']
    count = 0
    for detector_group in detectors:
        for detector in detector_group:
            count += _get_vehicle_count(conn, detector)
    return count


def _get_waiting_peds(conn, crossing_id: str, waiting_edge: str) -> list[float]:
    # get time waiting of pedestrians waiting to use a crossing 
    possible_peds = conn.edge.getLastStepPersonIDs(waiting_edge)
    group = []
    for ped in possible_peds:
        if conn.person.getNextEdge(ped) == crossing_id:
            group.append(conn.person.getWaitingTime(ped))
    return group


def _get_peds_exiting(conn, crossing_id: str, exit_edge_ids: tuple[str, str], threshold: float = 1.5) -> int:
    # get the number of pedestrians exiting the crossing
    edge_length = conn.lane.getLength(crossing_id + '_0')
    crossing_peds = conn.edge.getLastStepPersonIDs(crossing_id)
    count = 0
    for ped in crossing_peds:
        next_edge = conn.person.getNextEdge(ped)
        ped_pos = conn.person.getLanePosition(ped)
        if next_edge == exit_edge_ids[0]:
            remaining = edge_length - ped_pos
        else:
            remaining = ped_pos
        if remaining <= threshold:
            count += 1
    return count


def get_all_waiting_peds(conn, tls: str) -> list[list[float]]:
    # return the waiting pedestrians at the specified crossings
    crossings = TLS_IDS[tls]['crossings']
    waiting_peds = []
    for crossing in crossings:
        group = []
        waiting_edges = crossing[1:]
        for waiting_edge in waiting_edges:
            group.append(_get_waiting_peds(conn, crossing[0], waiting_edge))
        waiting_peds.append(group)
    return waiting_peds


def get_peds_throughput(conn, tls: str) -> list[int]:
    # return the number of pedestrians that have just finished crossing
    crossings = TLS_IDS[tls]['crossings']
    count = 0
    for crossing in crossings:
        count += _get_peds_exiting(conn, crossing[0], crossing[1:])
    return count


def get_blank_state(tls: str, compression: Compression = Compression.C2) -> tuple[int, ...]:
    # return the state for a TLS with placeholder values
    tls_phase = [-1]
    
    compression = _to_compression_enum(compression)

    if compression.value > Compression.C1.value:
        veh = [-1, -1]
        ped = [-1]
    else:
        waiting_vehicles = TLS_IDS[tls]['queues']
        veh = []
        for detector_group in waiting_vehicles:
            if compression.value > Compression.C0.value:
                veh.append(-1)
            else:
                n = max(1, len(detector_group))
                veh.extend(-1 for _ in range(n))

        waiting_peds = TLS_IDS[tls]['crossings']
        ped = []
        for ped_group in waiting_peds:
            if compression.value > Compression.C0.value:
                ped.append(-1)
            else:
                # uncompressed state -- 2 possible directions for pedestrians using a crossing
                ped.extend((-1, -1))
    
    return tuple(tls_phase + veh + ped)


def get_state(conn, tls: str, compression: Compression = Compression.C2) -> tuple[int, ...]:
    # get current phase of traffic light system
    tls_phase = get_current_tls_phase(conn, tls)

    compression = _to_compression_enum(compression)

    # get number of vehicles waiting in each queue
    waiting_vehicles = get_all_waiting_vehicles(conn, tls)
    veh = []
    for detector_group in waiting_vehicles:
        if compression.value > Compression.C0.value:
            vehicles = sum(detector_group, [])
            veh.append(len(vehicles))
        else:
            # full uncompressed state
            if not detector_group:
                veh.append(0)
                continue
            for vehicles in detector_group:
                veh.append(len(vehicles))

    # get number of pedestrians waiting to use each crossing
    waiting_peds = get_all_waiting_peds(conn, tls)
    ped = []
    for ped_group in waiting_peds:
        if compression.value > Compression.C0.value:
            peds = sum(ped_group, [])
            ped.append(len(peds))
        else:
            # full uncompressed state
            for peds in ped_group:
                ped.append(len(peds))

    if compression.value > Compression.C1.value:
        # combine 4 pedestrian areas into one, combine north and south bound, combine west and east bound
        veh = [veh[0] + veh[2], veh[1] + veh[3]]
        ped = [sum(ped)]

        # discretize to limit number of distinct values/combinations
        veh = _discretize(veh, thresholds=(0, 6, 12))
        ped = _discretize(ped, thresholds=(0, 12, 24))

    return (tls_phase, ) + tuple(veh) + tuple(ped)