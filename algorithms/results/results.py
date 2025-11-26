import numpy as np
import matplotlib.pyplot as plt

FILE_A = 'fixed_timer.txt'
FILE_B = 'q_learning.txt'


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

        print(len(local))

        cleaned[i] = np.nanmean(local)

    return cleaned


# read python-style lists from text files
with open(FILE_A, 'r') as f:
    a_list = eval(f.readlines()[0])

with open(FILE_B, 'r') as f:
    b_list = eval(f.readlines()[0])

a_list = moving_average(remove_outliers_rolling(a_list))
b_list = moving_average(remove_outliers_rolling(b_list))

# plot both lists
plt.figure()
plt.plot(a_list, label=f'{FILE_A}')
plt.plot(b_list, label=f'{FILE_B}')
plt.xlabel('Epoch')
plt.ylabel('Reward')
plt.title('TLS methods')
# plt.grid(True)
plt.legend()
plt.show()