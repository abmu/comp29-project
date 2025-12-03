# TODO
# - Complete DQN
# - Examine using traffic lights vs zebra crossings
# - Extend network, and think about network communication with the traffic light systems to improve performance
#
# Implement evaluation framework
# - Run each algorithm in parallel on the same dataset -- Fixed number of episodes, start a new traci siumlation, change route once every algorithm finishes that episode
# - Evaluate performance in new seeds, with different traffic densities (more/less pedestrians, more/less vehicles)
# - Comment on different weights to prioritise either pedestrians or vehicles (currently equal)
# - Explore other methods such as other Q-learning techniques (Double DQN, Dueling DQN) and actor-critic