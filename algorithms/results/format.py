import numpy as np

NET_NAME = 'demo'
MODE = 'train'
file = 'ft.txt'

results_file = f'{NET_NAME}/{MODE}/' + file

with open(results_file, 'r') as f:
    lst = eval(f.readlines()[0])

with open('temp.txt', 'w') as f:
    for n in lst:
        f.write(str(n) + '\n')
