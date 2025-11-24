import matplotlib.pyplot as plt


# TODO
# Use pypy3 to try improve performance


FILE_A = 'fixed_timer.txt'
FILE_B = 'q_learning.txt'

# read python-style lists from text files
with open(FILE_A, 'r') as f:
    a_list = eval(f.readlines()[0])

with open(FILE_B, 'r') as f:
    b_list = eval(f.readlines()[0])

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