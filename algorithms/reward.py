import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci


# TODO: Add following rewards
# - Negative for total wait time for both pedestrians and vehicles
# - Negative for excessive phase switching


def get_reward(waiting_vehicles: list[int], waiting_peds: list[int]) -> float:
    # penalize higher average queue lengths and number of pedestrians waiting
    total_vehicles = sum(waiting_vehicles)
    total_peds = sum(waiting_peds)
    reward = -float(total_vehicles + 0.5*total_peds)
    return reward