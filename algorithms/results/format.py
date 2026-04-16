import numpy as np
from results import pretty_list

NET_NAME = 'demo'
MODE = 'eval'

files = [
    # 'zebra.txt',
    'ft.txt',
    # 'ql_c0.txt',
    # 'ql_c1.txt',
    'ql_c2.txt',
    # 'dqn_c0.txt',
    # 'dqn_c1.txt',
    # 'dqn_c2.txt',
    # 'cdqn_c0.txt',
    # 'cdqn_c1.txt',
    # 'cdqn_c2.txt',
]

for file in files:
    results_file = f'{NET_NAME}/{MODE}/' + file

    with open(results_file, 'r') as f:
        lst = eval(f.readlines()[0])
        lst = pretty_list(lst, mode=MODE)

    with open(f'{NET_NAME}_{MODE}_{file}', 'w') as f:
        for n in lst:
            f.write(str(n) + '\n')
