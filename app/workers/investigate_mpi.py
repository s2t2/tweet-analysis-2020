


import os

from mpi4py import MPI
import numpy as np

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

# class Config:
#     def __init__(self):
#         self.mu = MU
#         ...
#         self.random_seed = RANDOM_SEED

class ClusterManager:
    def __init__(self):
        self.node_name = MPI.Get_processor_name()
        self.intracomm = MPI.COMM_WORLD
        self.node_rank = self.intracomm.Get_rank()
        self.cluster_size = self.intracomm.Get_size()

        print("----------------------")
        print("CLUSTER MANAGER")
        print("----------------------")
        print(self.intracomm) #> <mpi4py.MPI.Intracomm object at 0x10ed94a70>
        #print(dict(self.intracomm.info)) #> {'mpi_assert_no_any_source': 'false', 'mpi_assert_allow_overtaking': 'false'}
        print("----------------------")
        print("NODE NAME:", self.node_name) #> 'MJs-MacBook-Air.local'
        print("NODE RANK:", self.node_rank) #> 0
        print("CLUSTER SIZE:", self.cluster_size) #> 1
        print("MAIN NODE?:", self.is_main_node) #> True

    @property
    def is_main_node(self):
        return self.node_rank + 1 == self.cluster_size


if __name__ == "__main__":

    manager = ClusterManager()

    screen_names = ["user1", "user2", "user3"] # TODO: fetch via graph.nodes
    bot_probabilities = dict.fromkeys(screen_names, 0.5) # no priors, set all at 0.5!
    print(bot_probabilities) #> {'user1': 0.5, 'user2': 0.5, 'user3': 0.5}

    counter = 0 # to be compared with N_ITERS
    while counter < N_ITERS:
        print("DOING STUFF HERE!")
        counter += 1







exit()





inDeg = G0.in_degree(weight='weight')
if(type(inDeg)!=dict):
    graph_in = dict((x,y) for x, y in inDeg)
else:
    graph_in = inDeg

outDeg = G0.out_degree(weight='weight')
if(type(outDeg)!=dict):
    graph_out = dict((x,y) for x, y in outDeg)
else :
    graph_out = outDeg

print("Starting get link data step")

link_data = getLinkDataRestrained(G0)

for n in G0.nodes():
    if n not in graph_in.keys():
        graph_in[n]=0
    if n not in graph_out.keys():
        graph_out[n]=0

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
