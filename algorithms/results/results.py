import numpy as np
import matplotlib.pyplot as plt

PREFIX = 'eval/'
FILE_A = f'{PREFIX}fixed_timer.txt'
FILE_B = f'{PREFIX}q_learning.txt'
FILE_C = f'{PREFIX}deep_q_learning.txt'


def moving_average(data: np.ndarray, w: int = 5) -> np.ndarray:
    # calculate the moving average of the data
    return np.convolve(data, np.ones(w) / w, mode='same')


def remove_outliers_rolling(data: np.ndarray, w: int = 20, thresh: float = 1.0) -> np.ndarray:
    # remove extreme outliers from data
    cleaned = data.copy()

    for i in range(len(data)):
        start = max(0, i - w // 2)
        end = min(len(data), i + w // 2)
        if w & 1:  # add 1 if odd
            end += 1

        local = data[start:end]
        mean = np.mean(local)
        std = np.std(local)

        if std == 0:  # flat region
            continue

        # mark extreme outliers as NaN
        if abs(data[i] - mean) > thresh * std:
            cleaned[i] = np.nan

    # replace NaN values with mean in window
    for i in range(len(data)):
        if not np.isnan(cleaned[i]):
            continue

        start = max(0, i - w // 2)
        end = min(len(data), i + w // 2)
        if w & 1:  # add 1 if odd
            end += 1

        local = data[start:end]
        cleaned[i] = np.nanmean(local)

    return cleaned

def to_float_array(lst: list[float | None]) -> np.ndarray:
    # convert list to a float array, replacing None with an np.nan value
    return np.array([np.nan if x is None else x for x in lst], dtype=float)


# read python-style lists from text files
with open(FILE_A, 'r') as f:
    a_list = eval(f.readlines()[0])

with open(FILE_B, 'r') as f:
    b_list = eval(f.readlines()[0])

with open(FILE_C, 'r') as f:
    c_list = eval(f.readlines()[0])

epochs = np.arange(1, len(a_list) + 1)
a_list = moving_average(remove_outliers_rolling(to_float_array(a_list)))
b_list = moving_average(remove_outliers_rolling(to_float_array(b_list)))
c_list = moving_average(remove_outliers_rolling(to_float_array(c_list)))

# plot both lists
plt.figure()
plt.plot(epochs, a_list, label=f'{FILE_A}')
plt.plot(epochs, b_list, label=f'{FILE_B}')
plt.plot(epochs, c_list, label=f'{FILE_C}')
plt.xlabel('Epoch')
plt.ylabel('Reward')
plt.title('TLS methods')
# plt.grid(True)
plt.legend()
plt.show()