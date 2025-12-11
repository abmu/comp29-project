import numpy as np


current_cache = []


def get_cache() -> list[list[float | int]]:
    # get the cache
    return current_cache


def compute_stats(cache: list[list[float | int]]) -> dict[str, dict[str, float | int]]:
    # compute the mean and standard deviation of the cache values used when calculating the reward at each step
    arr = np.array(cache)  # shape: [N, 4]
    veh_delay = arr[:,0]
    veh_throughput = arr[:,1]
    ped_delay = arr[:,2]
    ped_throughput = arr[:,3]

    stats = {
        'veh_delay': {
            'mean': float(veh_delay.mean()),
            'std': float(veh_delay.std()),
            'min': float(veh_delay.min()),
            'max': float(veh_delay.max()),
            'sum': float(veh_delay.sum()),
            'len': len(veh_delay)
        },
        'veh_throughput': {
            'mean': float(veh_throughput.mean()),
            'std': float(veh_throughput.std()),
            'min': float(veh_throughput.min()),
            'max': float(veh_throughput.max()),
            'sum': float(veh_throughput.sum()),
            'len': len(veh_throughput)
        },
        'ped_delay': {
            'mean': float(ped_delay.mean()),
            'std': float(ped_delay.std()),
            'min': float(ped_delay.min()),
            'max': float(ped_delay.max()),
            'sum': float(ped_delay.sum()),
            'len': len(ped_delay)
        },
        'ped_throughput': {
            'mean': float(ped_throughput.mean()),
            'std': float(ped_throughput.std()),
            'min': float(ped_throughput.min()),
            'max': float(ped_throughput.max()),
            'sum': float(ped_throughput.sum()),
            'len': len(ped_throughput)
        }
    }

    return stats


def get_reward(waiting_vehicles: list[list[float]], waiting_peds: list[list[float]], vehicle_throughput: list[int], pedestrian_throughput: list[int]) -> float:
    # reward vehicle and pedestrian throughput, and penalise delays
    waiting_vehicles = [wait_time for vehicles in waiting_vehicles for wait_time in vehicles]
    veh_delay = sum(waiting_vehicles)
    veh_throughput = sum(vehicle_throughput)

    waiting_peds = [wait_time for peds in waiting_peds for wait_time in peds]
    ped_delay = sum(waiting_peds)
    ped_throughput = sum(pedestrian_throughput)

    # current_cache.append([veh_delay, veh_throughput, ped_delay, ped_throughput])

    # weights -- calculated from 'cache_stats.txt' file
    a = - (1.0 / 55.24)  # total current vehicle delay
    b = 1 / 0.20  # vehicle throughput
    c = - (1.0 / 156.07)  # total current pedestrian delay
    d = 1 / 0.18  # pedestrian throughput

    reward = (
        a * veh_delay +
        b * veh_throughput +
        c * ped_delay +
        d * ped_throughput
    )

    return reward