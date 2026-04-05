import numpy as np
import matplotlib.pyplot as plt

NET_NAME = 'demo'
MODE = 'eval'

files = [
    # 'zebra.txt',
    'ft.txt',
    'ql_c0.txt',
    'ql_c1.txt',
    'ql_c2.txt',
    # 'dqn_c0.txt',
    # 'dqn_c1.txt',
    # 'dqn_c2.txt',
    # 'cdqn_c0.txt',
    # 'cdqn_c1.txt',
    # 'cdqn_c2.txt',
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


def pretty_list(lst: list[float | None], mode: str = MODE) -> np.ndarray:
    # clean up list data
    lst = to_float_array(lst)
    if mode == 'train':
        lst = remove_outliers_rolling(lst)
        lst = moving_average(lst)
    elif mode == 'eval':
        EVAL_CONFIGS = 5
        EVAL_ROUTES_PER = 20

        lst = np.array(lst)

        # sanity check (optional but recommended)
        assert len(lst) == EVAL_CONFIGS * EVAL_ROUTES_PER, \
            f"Expected {EVAL_CONFIGS * EVAL_ROUTES_PER} elements, got {len(lst)}"

        # reshape into (5, 20)
        chunks = lst.reshape(EVAL_CONFIGS, EVAL_ROUTES_PER)

        # sort each row
        chunks_sorted = np.sort(chunks, axis=1)

        # take median of each row
        lst = np.median(chunks_sorted, axis=1)

    return lst


if __name__ == "__main__":
    lists = []
    # read python-style lists from text files
    for file in files:    
        with open(f'{NET_NAME}/{MODE}/' + file, 'r') as f:
            lst = eval(f.readlines()[0])
            # lst[10:20] = [0] * 7
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
