import numpy as np
from results import pretty_list

NET_NAME = 'demo'
MODE = 'eval'
file = 'ql_c0.txt'

results_file = f'{NET_NAME}/{MODE}/' + file

with open(results_file, 'r') as f:
    lst = eval(f.readlines()[0])
    lst = pretty_list(lst, mode=MODE)

with open(f'{NET_NAME}_{MODE}_{file}', 'w') as f:
    for n in lst:
        f.write(str(n) + '\n')
