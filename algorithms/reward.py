import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))

cache = []


def get_reward(waiting_vehicles: list[list[float]], waiting_peds: list[list[float]], vehicle_throughput: list[int], peds_throughput: list[int]) -> float:
    # reward vehicle and pedestrian throughput, and penalise delays
    waiting_vehicles = [wait_time for vehicles in waiting_vehicles for wait_time in vehicles]
    veh_delay = sum(waiting_vehicles)
    veh_throughput = sum(vehicle_throughput)

    waiting_peds = [wait_time for peds in waiting_peds for wait_time in peds]
    ped_delay = sum(waiting_peds)
    ped_throughput = sum(peds_throughput)

    cache.append([veh_delay, veh_throughput, ped_delay, ped_throughput])

    # weights
    a = -1.0
    b = -1.0
    c = 1
    d = 1

    reward = (
        a * veh_delay +
        b * ped_delay +
        c * veh_throughput +
        d * ped_throughput
    )

    return reward