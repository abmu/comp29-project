import os
import sys

if not os.environ.get('SUMO_HOME'):
    raise EnvironmentError('SUMO_HOME is not set.')
sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import traci


# TODO
# Add a reward parameter which penalises the amount of phase switches made


def get_reward(waiting_vehicles: list[list[float]], waiting_peds: list[list[float]]) -> float:
    # calculate reward -- penalize higher queue lengths, number of pedestrians waiting, and wait times
    waiting_vehicles = [wait_time for vehicles in waiting_vehicles for wait_time in vehicles]
    vehicles_count = len(waiting_vehicles)
    vehicles_wait = sum(waiting_vehicles)
    avg_veh_wait = vehicles_wait / vehicles_count if vehicles_count > 0 else 0.0
    max_veh_wait = max(waiting_vehicles) if vehicles_count > 0 else 0.0

    waiting_peds = [wait_time for peds in waiting_peds for wait_time in peds]
    peds_count = len(waiting_peds)
    peds_wait = sum(waiting_peds)
    avg_ped_wait = peds_wait / peds_count if peds_count > 0 else 0.0
    max_ped_wait = max(waiting_peds) if peds_count > 0 else 0.0

    # weights
    a = 1.0 # vehicle count
    b = 0.0 # average vehicle wait
    c = 0.0 # total vehicle wait
    d = 0.5 # pedestrian count
    e = 0.0 # average pedestrian wait
    f = 0.0 # total pedestrian wait

    reward = -(
        a * vehicles_count +
        b * avg_veh_wait +
        c * vehicles_wait +
        d * peds_count +
        e * avg_ped_wait +
        f * peds_wait
    )

    return reward