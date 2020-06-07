#################################################################################
################################# IMPORTS #######################################
#################################################################################
## BASIC
import os
import sys
import math
import datetime
import random
import numpy as np
import networkx as nx
## OWN
from ioHELPER import *
from networkClassifierHELPER import *
## PARALLELIZE JOBS
from mpi4py import MPI

###################################################################################
################################# SETUP MPI #######################################
###################################################################################
nproc = MPI.COMM_WORLD.Get_size() # Size of communicator
rank  = MPI.COMM_WORLD.Get_rank() # Ranks in communicator
inode = MPI.Get_processor_name() # Node where this MPI process runs
comm = MPI.COMM_WORLD


#################################################################################################
################################# READ INPUT HYPERPARAMS  #######################################
#################################################################################################
mu = float(sys.argv[1]) ##this is called gamma in the paper
alpha1 = float(sys.argv[2]) ##alpha_1 in the paper
alpha2 = float(sys.argv[3]) ##alpha_2 in the paper
iterations = int( sys.argv[4]) ##number of iterations (=1 cut/classify iteration in paper)
db = sys.aragv[5] ##name of the database/event studied (must match the DB_NAME name in RT_grahs/DB_NAME_G0_RT_GRAPH.csv)
mode = sys.argv[6] ##choose the prior to use : no prior, botometer scores, random scores, verified accounts, friends/fol ratio/score 
alambda1 = float(sys.argv[7]) ##lamba11 parameter in paper, chosen equal to 0.8
alambda2 = float(sys.argv[8])##lambda00 parameter in paper, chose equal to  0.6
epsilon = 10**(-float(sys.argv[9]))##named delta in paper, should be close to 0 (eg. 0.001) in order for lambda10 to be slightly > to lambda00+lambda11-1.
SEED = int(sys.argv[10])
alpha=[mu,alpha1,alpha2]


##Sanity Check
print('Here')

######################################################################################################
################################# READ INPUT RETWEET GRAPH  ##########################################
######################################################################################################
G0=readCSVFile_G('RT_graphs/'+db+'_G0_RT_GRAPH.csv')
##create directories for storing processor wise results
if not os.path.exists('./'+db+'_subGraphs'):
    os.makedirs('./'+db+'_subGraphs')
if not os.path.exists('./network_piBots_'+db):
    os.makedirs('./network_piBots_'+db)

##split all users in batches
all_users = sorted(list(G0.nodes()))
totUsers = len(all_users)
batch_size = int(totUsers/(nproc-1))


##non master processors compute the local probability of being on either side ot the cut
all_users = sorted(list(G0.nodes()))
totUsers = len(all_users)
batch_size = int(totUsers/(nproc-1))

if(rank !=nproc-1):
	countC = 0 
	while(True and countC < iterations):

		local_piBot={}
		ready = comm.recv(source=nproc-1)

		PL=[int(i) for i in readCustomFile('./'+db+'_subGraphs/PL_mu_'+str(mu)+'_alpha1_'+str(alpha1)+'_alpha2_'+str(alpha2)+'_lambda1_'+str(alambda1)+'_lambda2_'+str(alambda2)+'_epsilon_'+str(epsilon)+'_mode_'+mode+'.csv')]
		H=readCSVFile_H('./'+db+'_subGraphs/H_mu_'+str(mu)+'_alpha1_'+str(alpha1)+'_alpha2_'+str(alpha2)+'_lambda1_'+str(alambda1)+'_lambda2_'+str(alambda2)+'_epsilon_'+str(epsilon)+'_mode_'+mode+'_'+str(0)+'.csv')
		if(rank<nproc-2):
			subUsers = all_users[rank*batch_size:(rank+1)*batch_size] 
		else :
			subUsers = all_users[rank*batch_size:] 

		print(rank, 'gotya, I have ', len(subUsers), ' accounts to compute')
		count=0
		for node in subUsers:
			neighbors=list(np.unique([i for i in nx.all_neighbors(H,node) if i not in [0,1]])) 
			ebots=list(np.unique(np.intersect1d(neighbors,PL))) 
			ehumans=list(set(neighbors)-set(ebots)) 
			psi_l= sum([H[node][j]['capacity'] for j in ehumans])- sum([H[node][i]['capacity'] for i in ebots]) 
			psi_l_bis= psi_l + H[node][0]['capacity'] - H[1][node]['capacity'] ##proba to be in 1 = notPL

			if (psi_l_bis)>12:
				local_piBot[node] = 0
			else:
				local_piBot[node] = 1./(1+np.exp(psi_l_bis)) #Probability in the target (0) class

		print(rank, 'done, there you go ')
		comm.send(local_piBot, dest=nproc-1)
		countC +=1



##master processor first sends cut info, then aggregates results of local pibots from other processors
if(rank==nproc-1):
	
	np.random.seed(SEED)
	countP=0
	piBot = dict.fromkeys(all_users,0.5)

	##base mode = no prior = all accounts set to proba bot=0.5 at beginning
	piBot = dict.fromkeys(all_users,0.5)

	##different modes for different priors.
	##use botometer scores
	if(mode=='boto'):
		boto = readCustomDic_Pibot('botometer_scores/'+db+'_fullBotometer_piBots.csv')
		med = np.median(list(boto.values()))	

		for i in piBot:
			if(i in boto):
				piBot[i]=boto[i]
			else:
				piBot[i]=med		


	##random priors
	elif(mode=='random_unif'):
		rand=np.random.uniform(0,1,len(piBot))
		piBot=dict(zip(all_users,rand))

	elif(mode=='random_gauss'):
		rand=np.random.normal(0.5,0.1,len(piBot))
		piBot=dict(zip(all_users,rand))
	
	##############################	
	###### Perform the cut ######
	##############################	
	while(True and countP < iterations):

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
		

MPI.Finalize()

















