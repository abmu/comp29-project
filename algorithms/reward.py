import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci


# TODO
# - Add a reward parameter which penalises the amount of phase switches made
# Add OVERALL REWARD
# - Number of cars that went through the entire route
# - Number of pedestrians that went through
# - Average weight


def get_reward(waiting_vehicles: list[list[float]], waiting_peds: list[list[float]], vehicle_throughput: list[int], peds_throughput: list[int]) -> float:
    print(vehicle_throughput, peds_throughput)
    # calculate reward -- penalize higher queue lengths, number of pedestrians waiting, and wait times
    waiting_vehicles = [wait_time for vehicles in waiting_vehicles for wait_time in vehicles]
    vehicles_count = len(waiting_vehicles)
    veh_delay = sum(waiting_vehicles)

    waiting_peds = [wait_time for peds in waiting_peds for wait_time in peds]
    peds_count = len(waiting_peds)
    ped_delay = sum(waiting_peds)

    # weights
    a = -1.0
    b = -1.0

    reward = (
        a * veh_delay +
        b * ped_delay
    )

    return reward