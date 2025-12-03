# TODO
#
# Algorithms
# - Complete DQN
# - Examine using traffic lights vs zebra crossings
# - Extend network, and think about network communication with the traffic light systems to improve performance
#
# Implement evaluation framework
# - Run each algorithm in parallel on the same dataset -- Fixed number of episodes, start a new traci siumlation, change route once every algorithm finishes that episode
# - Evaluate performance in new seeds, with different traffic densities (more/less pedestrians, more/less vehicles)
# - Comment on different weights to prioritise either pedestrians or vehicles (currently equal)
# - Explore other methods such as other Q-learning techniques (Double DQN, Dueling DQN) and actor-critic
#
# State
# - Get full in-depth state with distinction between cars and bicycles, and direction of pedestrians on crossings, phase durations, etc.
#
# Routes
# - BUG: fix bug in network where bikes at CJ_1 can sometimes cause congestion, e.g. route 388 -- try widen distance between bike paths
# - Improve pedestrians accuracy by varying fringe-factor -- simulates pedestrians going into/out of buildings
# - Manually adjust weight of edges to make certain edges more likely to spawn, rather than random choice -- simulates commonly used/ main roads