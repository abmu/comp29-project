# TODO
#
# Report
# - Write introduction (in LaTeX)
#
# Algorithms
# - Examine using traffic lights vs zebra crossings
# - Extend network, and think about network communication with the traffic light systems to improve performance
#
# Implement evaluation framework
# - Evaluate performance in new seeds, with different traffic densities (more/less pedestrians, more/less vehicles)
# - Comment on different weights to prioritise either pedestrians or vehicles (currently equal) -- test max pedestrian priority, or max vehicle -- empirically what would be the best choice (average number of people per one vehicle vs one pedestrian)
# - Explore other methods such as other Q-learning techniques (Double DQN, Dueling DQN) and actor-critic
#
# State
# - Test Q learning with uncompressed vs current compressed state
# - Get full in-depth state with distinction between cars and bicycles, and direction of pedestrians on crossings, phase durations, etc.
#
# Routes
# - BUG: fix bug in network where bikes at CJ_1 can sometimes cause congestion, e.g. route 388 -- try widen distance between bike paths
# - Improve pedestrians accuracy by varying fringe-factor -- simulates pedestrians going into/out of buildings
# - Manually adjust weight of edges to make certain edges more likely to spawn, rather than random choice -- simulates commonly used/ main roads