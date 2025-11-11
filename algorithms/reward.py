import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci


# TODO
# Improve reward system by adding the following:
# - negative for total wait time for both pedestrians and vehicles


def get_reward(waiting_vehicles: list[int], waiting_peds: list[int]) -> float:
    # penalize higher average queue lengths and number of pedestrians waiting
    total_vehicles = sum(waiting_vehicles)
    total_peds = sum(waiting_peds)
    reward = -float(total_vehicles + 0.5*total_peds)
    return reward