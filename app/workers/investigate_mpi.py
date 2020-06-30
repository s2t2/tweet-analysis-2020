


import os
from pprint import pprint

from mpi4py import MPI
import numpy as np
from networkx import DiGraph

from app.botcode import parse_bidirectional_links, compute_joint_energy

# HYPERPARAMETERS

MU = float(os.getenv("MU", default="1")) # called "gamma" in the paper
ALPHA_1 = float(os.getenv("ALPHA_1", default="100"))
ALPHA_2 = float(os.getenv("ALPHA_2", default="100"))
ALPHA = [MU, ALPHA_1, ALPHA_2]

N_ITERS = int(os.getenv("N_ITERS", default="1"))
DIRNAME = os.getenv("DIRNAME", default="impeachment-dev")
PRIORS_MODE = os.getenv("PRIORS_MODE", default="normal") # should be one of ["boto", "random_unif", "random_gaus"]

LAMBDA_1 = float(os.getenv("LAMBDA_1", default="0.8")) # called "lamba11" in the paper
LAMBDA_2 = float(os.getenv("LAMBDA_2", default="0.6")) # called "lambda00" in the paper
EPSILON = float(os.getenv("EPSILON", default="0.001")) # called "delta" in the paper. should be close to 0 (eg. 0.001) in order for lambda10 to be slightly > (lambda00 + lambda11 - 1).

RANDOM_SEED = int(os.getenv("RANDOM_SEED", default="0")) # called "delta" in the paper. should be close to 0 (eg. 0.001) in order for lambda10 to be slightly > (lambda00 + lambda11 - 1).
np.random.seed(RANDOM_SEED)

class ClusterManager:
    def __init__(self):
        self.node_name = MPI.Get_processor_name()
        self.intracomm = MPI.COMM_WORLD
        self.node_rank = self.intracomm.Get_rank()
        self.cluster_size = self.intracomm.Get_size()

        print("----------------------")
        print("CLUSTER MANAGER")
        #print("----------------------")
        #print(self.intracomm) #> <mpi4py.MPI.Intracomm object at 0x10ed94a70>
        #print(dict(self.intracomm.info)) #> {'mpi_assert_no_any_source': 'false', 'mpi_assert_allow_overtaking': 'false'}
        #print("----------------------")
        print("   NODE NAME:", self.node_name) #> 'MJs-MacBook-Air.local'
        print("   NODE RANK:", self.node_rank) #> 0
        print("   CLUSTER SIZE:", self.cluster_size) #> 1
        print("   MAIN NODE?:", self.is_main_node) #> True

    @property
    def is_main_node(self):
        return self.node_rank + 1 == self.cluster_size

def mock_weighted_graph():
    graph = DiGraph()
    rows = [
        # add some examples of users retweeting others:
        {"user_screen_name": "user1", "retweet_user_screen_name": "leader1", "retweet_count": 4},
        {"user_screen_name": "user2", "retweet_user_screen_name": "leader1", "retweet_count": 6},
        {"user_screen_name": "user3", "retweet_user_screen_name": "leader2", "retweet_count": 4},
        {"user_screen_name": "user4", "retweet_user_screen_name": "leader2", "retweet_count": 2},
        {"user_screen_name": "user5", "retweet_user_screen_name": "leader3", "retweet_count": 4},
        # add some examples of users retweeting eachother:
        {"user_screen_name": "colead1", "retweet_user_screen_name": "colead2", "retweet_count": 3},
        {"user_screen_name": "colead2", "retweet_user_screen_name": "colead1", "retweet_count": 2},
        {"user_screen_name": "colead3", "retweet_user_screen_name": "colead4", "retweet_count": 1},
        {"user_screen_name": "colead4", "retweet_user_screen_name": "colead3", "retweet_count": 4},
        # and users tweeting them as well:
        {"user_screen_name": "user1", "retweet_user_screen_name": "colead1", "retweet_count": 4},
        {"user_screen_name": "user2", "retweet_user_screen_name": "colead1", "retweet_count": 6},
        {"user_screen_name": "user3", "retweet_user_screen_name": "colead3", "retweet_count": 4},
        {"user_screen_name": "user4", "retweet_user_screen_name": "colead3", "retweet_count": 2},
        {"user_screen_name": "user5", "retweet_user_screen_name": "colead4", "retweet_count": 4},
    ]
    for row in rows:
        graph.add_edge(row["user_screen_name"], row["retweet_user_screen_name"], rt_count=float(row["retweet_count"]))
    return graph

if __name__ == "__main__":

    # manager = ClusterManager()

    # counter = 0 # to be compared with N_ITERS
    # while counter < N_ITERS:
    #     print("DOING STUFF HERE!")
    #     counter += 1

    weighted_graph = mock_weighted_graph()

    print("----------------------")
    nodes = list(weighted_graph.nodes) #> ["user1", "user2", "user3", etc.]
    bot_probabilities = dict.fromkeys(nodes, 0.5) # no priors, set all at 0.5!
    print("BOT PROBABILITIES (PRIORS)") #> {'user1': 0.5, 'user2': 0.5, 'user3': 0.5}
    print(bot_probabilities)

    print("----------------------")
    in_degree = dict(weighted_graph.in_degree(weight="rt_count")) # sums by number of incoming RTs
    #> InDegreeView({'user1': 0, 'leader1': 10.0, 'user2': 0, 'user3': 0, 'leader2': 6.0, 'user4': 0, 'user5': 0, 'leader3': 4.0})
    in_degrees = dict(in_degree) # dict((k,v) for k,v in in_degree)
    print("IN-DEGREES", len(in_degrees))
    print(in_degrees)
    assert in_degrees == {'user1': 0, 'leader1': 10.0, 'user2': 0, 'user3': 0, 'leader2': 6.0, 'user4': 0, 'user5': 0, 'leader3': 4.0, 'colead1': 12.0, 'colead2': 3.0, 'colead3': 10.0, 'colead4': 5.0}
    assert len(in_degrees) == 12

    print("----------------------")
    out_degree = weighted_graph.out_degree(weight="rt_count") # sums by number of outgoing RTs
    #> OutDegreeView({'user1': 4.0, 'leader1': 0, 'user2': 6.0, 'user3': 4.0, 'leader2': 0, 'user4': 2.0, 'user5': 4.0, 'leader3': 0})
    out_degrees = dict(out_degree) # dict((k,v) for k,v in in_degree)
    print("OUT-DEGREES", len(out_degrees))
    print(out_degrees)
    assert out_degrees == {'user1': 8.0, 'leader1': 0, 'user2': 12.0, 'user3': 8.0, 'leader2': 0, 'user4': 4.0, 'user5': 8.0, 'leader3': 0, 'colead1': 3.0, 'colead2': 2.0, 'colead3': 1.0, 'colead4': 4.0}
    assert len(out_degrees) == 12

    # IS THIS NECESSARY?
    print("----------------------")
    print("ENSURING ALL NODES ARE REPRESENTED IN IN-DEGREE AND OUT-DEGREE VIEWS...")
    for node in weighted_graph.nodes():
        if node not in in_degrees.keys():
            print("ADDING NODE TO IN-DEGREES")
            in_degrees[node] = 0
        if node not in out_degrees.keys():
            print("ADDING NODE TO OUT-DEGREES")
            out_degrees[node] = 0
    print("IN-DEGREES:", len(in_degrees))
    print("OUT-DEGREES:", len(out_degrees))
    assert len(in_degrees) == 12
    assert len(out_degrees) == 12

    print("----------------------")
    print("GATHERING LINKS...")
    links = parse_bidirectional_links(weighted_graph)
    pprint(links)
    #for link in links:
    #    print(link) #> ['user1', 'leader1', True, False, 4.0, 0]
    assert links == [
        ['user1', 'leader1', True, False, 4.0, 0],
        ['user1', 'colead1', True, False, 4.0, 0],
        ['user2', 'leader1', True, False, 6.0, 0],
        ['user2', 'colead1', True, False, 6.0, 0],
        ['user3', 'leader2', True, False, 4.0, 0],
        ['user3', 'colead3', True, False, 4.0, 0],
        ['user4', 'leader2', True, False, 2.0, 0],
        ['user4', 'colead3', True, False, 2.0, 0],
        ['user5', 'leader3', True, False, 4.0, 0],
        ['user5', 'colead4', True, False, 4.0, 0],
        ['colead1', 'colead2', True, True, 3.0, 2.0],
        ['colead2', 'colead1', True, True, 2.0, 3.0],
        ['colead3', 'colead4', True, True, 1.0, 4.0],
        ['colead4', 'colead3', True, True, 4.0, 1.0]
    ]

    print("----------------------")
    print("COMPUTING ENERGIES...")
    energies = [(
        link[0],
        link[1],
        compute_joint_energy(link[0], link[1], link[4], in_degrees, out_degrees, ALPHA, LAMBDA_1, LAMBDA_2, EPSILON)
    ) for link in links]
    pprint(energies)
    assert energies == [
        ('user1', 'leader1', [0.0, 0, 0.0, 0.0]),
        ('user1', 'colead1', [0.0, 0, 0.0, 0.0]),
        ('user2', 'leader1', [0.0, 0, 0.0, 0.0]),
        ('user2', 'colead1', [0.0, 0, 0.0, 0.0]),
        ('user3', 'leader2', [0.0, 0, 0.0, 0.0]),
        ('user3', 'colead3', [0.0, 0, 0.0, 0.0]),
        ('user4', 'leader2', [0.0, 0, 0.0, 0.0]),
        ('user4', 'colead3', [0.0, 0, 0.0, 0.0]),
        ('user5', 'leader3', [0.0, 0, 0.0, 0.0]),
        ('user5', 'colead4', [0.0, 0, 0.0, 0.0]),
        ('colead1', 'colead2', [0.0, 0, 0.0, 0.0]),
        ('colead2', 'colead1', [0.0, 0, 0.0, 0.0]),
        ('colead3', 'colead4', [0.0, 0, 0.0, 0.0]),
        ('colead4', 'colead3', [0.0, 0, 0.0, 0.0])
    ]

    breakpoint()

    # ease computations by only keeping edges with non zero weight
    print("----------------------")
    weighty_energies = [e for e in energies if sum(e[2]) > 0]
    print("ENERGIES WITH POSITIVE BIDIRECTIONAL WEIGHTS:",  len(weighty_energies))
    for we in weighty_energies:
        print(we)

    # TODO: update dataset to include some reverse RTs to get some energies to use at this point!

exit()


H, PL, user_data = computeH(G0, piBot, edgelist_data, graph_out, graph_in)
print(rank, 'Completed graph cut, send it to children')

pl_filepath = './'+db+'_subGraphs/PL_mu_'+str(mu)+'_alpha1_'+str(alpha1)+'_alpha2_'+str(alpha2)+'_lambda1_'+str(alambda1)+'_lambda2_'+str(alambda2)+'_epsilon_'+str(epsilon)+'_mode_'+mode+'.csv'
h_filepath = './'+db+'_subGraphs/H_mu_'+str(mu)+'_alpha1_'+str(alpha1)+'_alpha2_'+str(alpha2)+'_lambda1_'+str(alambda1)+'_lambda2_'+str(alambda2)+'_epsilon_'+str(epsilon)+'_mode_'+mode+'_'+str(0)+'.csv'
writeCSVFile(pl_fiepath, PL)
writeCSVFile_H(h_filepath, H)

##send a flag to children processors to start computing local pibot
for i in range(0,nproc-2):
    comm.send(True, dest=i)

comm.send(True, dest=nproc-2)

##receive results from children and aggregate
print(rank, 'ready to receive')
gather=[]
for i in range(0,nproc-1):
    r = comm.recv(source=i)
    gather.append(r)
    print(rank, ' received from ', i)

users = list(user_data.keys())

clustering =dict.fromkeys(users,0)
for user in PL:
    user_data[user]['clustering'] = 1
    clustering[user] = 1

print(rank, ' received ', len(gather), ' local piBots')
piBot = {}
for d in gather:
    for user in d:
        piBot[user] = d[user]

##write result of aggregation. Clustering= hard score, piBot= continuous score between 0 and 1 (pick threshold)
writeCSVFile_piBot('./network_piBots_'+db+'/ntwk_piBot_mu_'+str(mu)+'_alpha1_'+str(alpha1)+'_alpha2_'+str(alpha2)+'_lambda1_'+str(alambda1)+'_lambda2_'+str(alambda2)+'_epsilon_'+str(epsilon)+'_mode_'+mode+'_iteration_'+str(countP)+'_SEED_'+str(SEED)+'.csv', piBot)
#writeCSVFile_piBot('./network_piBots_'+db+'/ntwk_clustering_mu_'+str(mu)+'_alpha1_'+str(alpha1)+'_alpha2_'+str(alpha2)+'_lambda1_'+str(alambda1)+'_lambda2_'+str(alambda2)+'_epsilon_'+str(epsilon)+'_mode_'+mode+'_iteration_'+str(countP)+'.csv', clustering)
countP += 1


# MPI.Finalize()
