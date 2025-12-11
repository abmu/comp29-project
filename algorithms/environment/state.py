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


def get_all_waiting_vehicles(conn, detectors: list[list[str]]) -> list[list[float]]:
    # return the waiting vehicles in the specified detectors
    waiting_vehicles = []
    for detector_group in detectors:
        group = []
        for detector in detector_group:
            group += _get_waiting_vehicles(conn, detector)
        waiting_vehicles.append(group)
    return waiting_vehicles


def get_vehicle_throughput(conn, detectors: list[list[str]]) -> list[int]:
    # return the vehicle count that have crossed the specified detectors
    throughput = []
    for detector_group in detectors:
        count = 0
        for detector in detector_group:
            count += _get_vehicle_count(conn, detector)
        throughput.append(count)
    return throughput


def _get_waiting_peds(conn, crossing_id: str, waiting_edge_ids: tuple[str, str]) -> list[float]:
    # get time waiting of pedestrians waiting to use a crossing 
    possible_peds = conn.edge.getLastStepPersonIDs(waiting_edge_ids[0]) + conn.edge.getLastStepPersonIDs(waiting_edge_ids[1])
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


def get_all_waiting_peds(conn, crossings: list[tuple[str, str, str]]) -> list[list[float]]:
    # return the waiting pedestrians at the specified crossings
    waiting_peds = []
    for crossing in crossings:
        group = _get_waiting_peds(conn, crossing[0], crossing[1:])
        waiting_peds.append(group)
    return waiting_peds


def get_peds_throughput(conn, crossings: list[tuple[str, str, str]]) -> list[int]:
    # return the number of pedestrians that have just finished crossing
    throughput = []
    for crossing in crossings:
        count = _get_peds_exiting(conn, crossing[0], crossing[1:])
        throughput.append(count)
    return throughput


def get_state(conn, tls: str, detectors: list[list[str]], crossings: list[tuple[str, str, str]]) -> tuple[int, ...]:
    # get current phase of traffic light system
    tls_phase = get_current_tls_phase(conn, tls)

    # get number of vehicles waiting in each queue
    waiting_vehicles = [len(vehicles) for vehicles in get_all_waiting_vehicles(conn, detectors)]

    # get number of pedestrians waiting to use each crossing
    waiting_peds = [len(peds) for peds in get_all_waiting_peds(conn, crossings)]

    # simplify state
    # combine 4 pedestrian areas into one, combine north and south bound, combine west and east bound
    waiting_peds = [sum(waiting_peds)]
    waiting_vehicles = [waiting_vehicles[0] + waiting_vehicles[2], waiting_vehicles[1] + waiting_vehicles[3]]

    # discretize to limit number of distinct values/combinations
    waiting_vehicles = _discretize(waiting_vehicles, thresholds=(0, 6, 12))
    waiting_peds = _discretize(waiting_peds, thresholds=(0, 12, 24))

    return (tls_phase, ) + tuple(waiting_vehicles) + tuple(waiting_peds)