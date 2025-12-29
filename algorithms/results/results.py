import numpy as np
import matplotlib.pyplot as plt

DIR_PREFIX = 'demo/train/'
files = [
    'fixed_timer.txt',
    'q_learning.txt',
    'deep_q_learning.txt',
    # 'q_learning_uncompressed.txt',
    'deep_q_learning_uncompressed.txt',
]


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


def pretty_list(lst: list[float | None]) -> np.ndarray:
    # clean up list data
    lst = to_float_array(lst)
    lst = remove_outliers_rolling(lst)
    lst = moving_average(lst)
    return lst


lists = []
# read python-style lists from text files
for file in files:    
    with open(DIR_PREFIX + file, 'r') as f:
        lst = eval(f.readlines()[0])
        lists.append(pretty_list(lst))

epochs = np.arange(1, len(lists[0]) + 1)

# plot both lists
plt.figure()
for i, file in enumerate(files):
    plt.plot(epochs, lists[i], label=f'{file}')
plt.xlabel('Epoch')
plt.ylabel('Reward')
plt.title('TLS methods')
# plt.grid(True)
plt.legend()
plt.show()