


import os

from mpi4py import MPI
import numpy as np
from networkx import DiGraph

#from start.botcode.networkClassifierHELPER import psi as compute_joint_energy

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
        {"user_screen_name": "user1", "retweet_user_screen_name": "leader1", "retweet_count": 4},
        {"user_screen_name": "user2", "retweet_user_screen_name": "leader1", "retweet_count": 6},
        {"user_screen_name": "user3", "retweet_user_screen_name": "leader2", "retweet_count": 4},
        {"user_screen_name": "user4", "retweet_user_screen_name": "leader2", "retweet_count": 2},
        {"user_screen_name": "user5", "retweet_user_screen_name": "leader3", "retweet_count": 4}
    ]
    for row in rows:
        graph.add_edge(row["user_screen_name"], row["retweet_user_screen_name"], rt_count=float(row["retweet_count"]))
    return graph



def compute_link_data(graph, weight_attr="rt_count"):
    """
    Computes the degree to which the users in each edge were retweeting eachother.

    Params: graph (networkx.DiGraph) a retweet graph with edges like: ("user", "retweeted_user", rt_count=10)
    """
    edges = graph.edges(data=True)
    #> OutEdgeDataView([('user1', 'leader1', {'rt_count': 4.0}), ('user2', 'leader1', {'rt_count': 6.0}), ('user3', 'leader2', {'rt_count': 4.0}), ('user4', 'leader2', {'rt_count': 2.0}), ('user5', 'leader3', {'rt_count': 4.0})])

    weighted_edges = dict(((x,y), z[weight_attr]) for x, y, z in edges)
    #> {('user1', 'leader1'): 4.0, ('user2', 'leader1'): 6.0, ('user3', 'leader2'): 4.0, ('user4', 'leader2'): 2.0, ('user5', 'leader3'): 4.0}

    links = []
    for k in weighted_edges:
            user = k[0] #> 'user1'
            retweeted_user = k[1] #> 'leader1'
            edge_weight = weighted_edges[k] #> 4.0

            reverse_edge_key = (retweeted_user, user)
            if(reverse_edge_key in weighted_edges.keys()):
                has_reverse_edge = True
                reverse_edge_weight = weighted_edges[reverse_edge_key]
            else:
                has_reverse_edge = False
                reverse_edge_weight = 0

            link = [
                user, retweeted_user,
                True, has_reverse_edge,
                edge_weight, reverse_edge_weight
            ] #> ['user1', 'leader1', True, False, 4.0, 0]
            links.append(link)
    #> [['user1', 'leader1', True, False, 4.0, 0], ['user2', 'leader1', True, False, 6.0, 0], ['user3', 'leader2', True, False, 4.0, 0], ['user4', 'leader2', True, False, 2.0, 0], ['user5', 'leader3', True, False, 4.0, 0]]
    return links



def compute_joint_energy(u1, u2, wlr, in_graph, out_graph, alpha, alambda1, alambda2, epsilon):
    """
    Compute joint energy potential between two users

	Params:
        u1 (int) ID of user u1
	    u2 (int) ID of user u2
	    wlr (int) number of retweets from u1 to u2
        out_graph (dict of ints) a graph that stores out degrees of accounts in retweet graph
        in_graph (dict of ints) a graph that stores in degrees of accounts in retweet graph
        alpha (list of floats) a list containing hyperparams mu, alpha1, alpha2
        alambda1 (float) value of lambda11
        alambda2 (float) value of lambda00
        epsilon (int) exponent such that delta=10^(-espilon), where lambda01=lambda11+lambda00-1+delta
	"""

    #here alpha is a vector of length three, psi decays according to a logistic sigmoid function
    val_00 = 0
    val_01 = 0
    val_10 = 0
    val_11 = 0

    if out_graph[u1]==0 or in_graph[u2]==0:
        print("Relationship problem: "+str(u1)+" --> "+str(u2))

    temp = alpha[1]/float(out_graph[u1])-1 + alpha[2]/float(in_graph[u2])-1
    if temp <10:
        val_01 =wlr*alpha[0]/(1+np.exp(temp))
    else:
        val_01=0

    val_10 = (alambda2+alambda1-1+epsilon)*val_01
    val_00 = alambda2*val_01
    val_11 = alambda1*val_01

    test2 = 0.5*val_11+0.25*(val_10-val_01)
    test3 = 0.5*val_00+0.25*(val_10-val_01)
    if(min(test2,test3)<0):
        print('PB EDGE NEGATIVE')
        val_00 = val_11 = 0.5*val_01

    if(val_00+val_11>val_01+val_10):
        print(u1,u2)
        print('psi01',val_01)
        print('psi11',val_11)
        print('psi00',val_00)
        print('psi10',val_10)
        print("\n")

    values = [val_00,val_01,val_10,val_11]
    return values;











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
    print("INCOMING RETWEETS")
    print(in_degrees)

    print("----------------------")
    out_degree = weighted_graph.out_degree(weight="rt_count") # sums by number of outgoing RTs
    #> OutDegreeView({'user1': 4.0, 'leader1': 0, 'user2': 6.0, 'user3': 4.0, 'leader2': 0, 'user4': 2.0, 'user5': 4.0, 'leader3': 0})
    out_degrees = dict(out_degree) # dict((k,v) for k,v in in_degree)
    print("OUTGOING RETWEETS")
    print(in_degrees)

    print("----------------------")
    print("GATHERING LINK DATA...")

    bidirectional_edge_weights = compute_link_data(weighted_graph)
    for link in bidirectional_edge_weights:
        print(link)


    print("----------------------")
    print("ENSURING ALL NODES ARE REPRESENTED IN IN-DEGREE AND OUT-DEGREE VIEWS...")
    for node in weighted_graph.nodes():
        if node not in in_degrees.keys():
            print("ADDING NODE TO IN-DEGREES")
            in_degrees[node] = 0
        if node not in out_degrees.keys():
            print("ADDING NODE TO OUT-DEGREES")
            out_degrees[node] = 0
    print("IN-DEGREES")
    print(in_degrees)
    print("OUT-DEGREES")
    print(out_degrees)








exit()







edgelist_data =[(i[0], i[1], psi(i[0],i[1],i[4],graph_in, graph_out,alpha,alambda1,alambda2,epsilon)) for i in link_data]
print("tot edgelist", len(edgelist_data))


##ease computations by only keeping edges with non zero weight
edgelist_data = [t for t in edgelist_data if sum(t[2]) > 0]
print("only > 0 edgelist", len(edgelist_data))

H, PL, user_data = computeH(G0, piBot, edgelist_data, graph_out, graph_in)
print(rank, 'completed graph cut, send it to children')
writeCSVFile('./'+db+'_subGraphs/PL_mu_'+str(mu)+'_alpha1_'+str(alpha1)+'_alpha2_'+str(alpha2)+'_lambda1_'+str(alambda1)+'_lambda2_'+str(alambda2)+'_epsilon_'+str(epsilon)+'_mode_'+mode+'.csv',PL)
writeCSVFile_H('./'+db+'_subGraphs/H_mu_'+str(mu)+'_alpha1_'+str(alpha1)+'_alpha2_'+str(alpha2)+'_lambda1_'+str(alambda1)+'_lambda2_'+str(alambda2)+'_epsilon_'+str(epsilon)+'_mode_'+mode+'_'+str(0)+'.csv',H)

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
