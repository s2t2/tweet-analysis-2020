import math
import networkx as nx
from collections import defaultdict
from operator import itemgetter
import numpy as np
import time
from ioHELPER import *

#####################################################################################################
####################### BUILD RETWEET NX-(SUB)GRAPH FROM DICTIONNARY ################################
#####################################################################################################
'''
Takes as input a csv file of retweet relationships and builds
a NetworkX object, in order to apply prebuilt mincut algorithms
'''
def buildRTGraph(graph, subNodes, lowerBound=0):
	'''
	INPUTS:
	## graph (csv file) 
		a csv file with ID of user retweeting, user retweeted, and number of retweets. (see README for more details)
	## subNodes (list of ints)
		a list of users IDs if you want to only consider a subgraph of the RT graph
	## lowerBound (int) 	
		an int to only consider retweet relationship if retweet count from User1 to User2 is above bound (sparsify graph)
	'''
	G = nx.DiGraph()
	count = 0
	firstInter = list(np.unique(np.intersect1d(subNodes, list(graph.keys()))))
	for node in firstInter:
		count+=1
		print("at user n" + str(count) + " on " + str(len(graph)))
		unique2, counts = np.unique(graph[node], return_counts=True)
		res = dict(zip(unique2, counts))
		inter = np.unique(np.intersect1d(unique2,subNodes))
		for i in inter:
			w=res[i]
			if(i!=node and w >= lowerBound):
				G.add_node(node)
				G.add_node(i)
				G.add_edge(node, i, weight = w)

	return G;


############################################################################
####################### BUILD/CUT ENERGY GRAPH #############################
############################################################################
'''
Takes as input the RT graph and builds the energy graph.
Then cuts the energy graph to classify
'''
def computeH(G, piBot ,edgelist_data, graph_out, graph_in):
	H=nx.DiGraph()
	'''
	INPUTS:
	## G (ntwkX graph) 
		the Retweet Graph from buildRTGraph
	## piBot (dict of floats)
		a dictionnary with prior on bot probabilities. Keys are users_ids, values are prior bot scores.
	## edgelist_data (list of  tuples) 	
		information about edges to build energy graph. 
		This list comes in part from the getLinkDataRestrained method
	## graph_out (dict of ints)
		a graph that stores out degrees of accounts in retweet graph
	## graph_in (dict of ints)
		a graph that stores in degrees of accounts in retweet graph

	'''
	user_data={i:{
				'user_id':i,
				'out':graph_out[i],
				'in':graph_in[i],
				'old_prob': piBot[i],
				'phi_0': max(0,-np.log(float(10**(-20)+(1-piBot[i])))), 
				'phi_1': max(0,-np.log(float(10**(-20)+ piBot[i]))),
				'prob':0,
				'clustering':0
						} for i in G.nodes()}
	
	set_1 = [(el[0],el[1]) for el in edgelist_data]
	set_2 = [(el[1],el[0]) for el in edgelist_data]
	set_3 = [(el,0) for el in user_data]
	set_4 = [(1,el) for el in user_data]

	H.add_edges_from(set_1+set_2+set_3+set_4,capacity=0)
	

	for i in edgelist_data:
		
		val_00 = i[2][0]
		val_01 = i[2][1]
		val_10 = i[2][2]
		val_11 = i[2][3]

		H[i[0]][i[1]]['capacity']+= 0.5*(val_01+val_10-val_00-val_11)
		H[i[1]][i[0]]['capacity'] += 0.5*(val_01+val_10-val_00-val_11)
		H[i[0]][0]['capacity'] += 0.5*val_11+0.25*(val_10-val_01)
		H[i[1]][0]['capacity'] += 0.5*val_11+0.25*(val_01-val_10)
		H[1][i[0]]['capacity'] += 0.5*val_00+0.25*(val_01-val_10)
		H[1][i[1]]['capacity'] += 0.5*val_00+0.25*(val_10-val_01) 


		if(H[1][i[0]]['capacity']<0):
			print("Neg capacity")
			break;
		if(H[i[1]][0]['capacity']<0):
			print("Neg capacity")
			break;
		if(H[1][i[1]]['capacity']<0):
			print("Neg capacity")
			break;
		if(H[i[0]][0]['capacity']<0):
			print("Neg capacity")
			break;

	for i in user_data.keys():
		H[1][i]['capacity'] += user_data[i]['phi_0']
		if(H[1][i]['capacity'] <0):
			print("Neg capacity");
			break;
			
		H[i][0]['capacity'] += user_data[i]['phi_1']
		if(H[i][0]['capacity'] <0):
			print("Neg capacity");
			break;
	cut_value,mc=nx.minimum_cut(H,1,0)
	PL=list(mc[0]) #the other way around
	if 1 not in PL:
		print("Double check")
		PL=list(mc[1])
	PL.remove(1) 

	return H, PL, user_data

###############################################################################
####################### COMPUTE EDGES INFORMATION #############################
###############################################################################
'''
Takes as input the RT graph and retrieves information on edges 
to further build H.
'''
def getLinkDataRestrained(G):
	'''
	INPUTS:
	## G (ntwkX graph) 
		the Retweet Graph from buildRTGraph
	'''
	edges = G.edges(data=True)
	e_dic = dict(((x,y), z['weight']) for x, y, z in edges)
	link_data = []
	for e in e_dic:
			i=e[0]
			j=e[1]
			rl=False
			wrl=0
			if((j,i) in e_dic.keys()):
				rl = True
				wrl = e_dic[(j,i)]
			link_data.append([i,j,True,rl, e_dic[e], wrl])
	return link_data;




##########################################################################
####################### POTENTIAL FUNCTION ###############################
##########################################################################
'''
Compute joint energy potential between two users
'''
def psi(u1, u2, wlr, in_graph, out_graph,alpha,alambda1,alambda2,epsilon):
	'''
	INPUTS:
	## u1 (int) 
		ID of user u1 
	## u2 (int) 
		ID of user u2
	## wlr (int) 
		number of retweets from u1 to u2
	## out_graph (dict of ints)
		a graph that stores out degrees of accounts in retweet graph
	## in_graph (dict of ints)
		a graph that stores in degrees of accounts in retweet graph
	## alpha (list of floats)
		a list containing hyperparams mu, alpha1, alpha2
	## alambda1 (float)
		value of lambda11
	## alambda2 (float)
		value of lambda00
	## epsilon (int)
		exponent such that delta=10^(-espilon), where lambda01=lambda11+lambda00-1+delta
	'''
	
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





