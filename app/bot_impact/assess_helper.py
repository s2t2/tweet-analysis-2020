import json,random,csv
import numpy as np
from scipy import sparse

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
#code for helper file

#create networkx graph object from node and edge list csv files
def G_from_edge_list(node_filename, edge_filename):
    G = nx.DiGraph()
    data_nodes = pd.read_csv(node_filename)
    for row in data_nodes.iterrows():
        G.add_node(row[1]['id'], Name = row[1]['id'],InitialOpinion=row[1]['InitialOpinion'],Stubborn = row[1]['Stubborn'],
                   Rate=row[1]['Rate'], FinalOpinion = row[1]['InitialOpinion'], Bot = row[1]['Bot'])

    data = pd.read_csv(edge_filename)
    for row in data.iterrows():
        following = row[1]['following']
        follower = row[1]['follower']
        rate = G.nodes[following]['Rate']
        #print("%s,%s %s"%(following,follower,rate))
        G.add_edge(following,follower,Rate=rate)
    return G

#create networkx graph object from node and follower graph csv files
#node file format is (id,InitialOpinion,Stubborn,rate,FinalOpinion,Bot)
#follower graph file format is (follower, following1,following2,following3,...)
def G_from_follower_graph(node_filename,follower_graph_filename,threshold_low,threshold_high):
    G = nx.DiGraph()
    print("Building network for Assess.\nStubborn intervals = (0,%.3f),(%.3f,1)"%(threshold_low,threshold_high))
    #first get the nodes and their info and add it to the graph object G
    data_nodes = pd.read_csv(node_filename)
    data_nodes.Stubborn = 1*np.logical_or(data_nodes.InitialOpinion<=threshold_low, data_nodes.InitialOpinion>=threshold_high)
    for row in data_nodes.iterrows():
        G.add_node(row[1]['id'], Name = row[1]['id'],InitialOpinion=row[1]['InitialOpinion'],Stubborn = row[1]['Stubborn'],
                   Rate=row[1]['Rate'], FinalOpinion = row[1]['InitialOpinion'], Bot = row[1]['Bot'])

    #second, add the edges to the graph if both nodes are in the node set
    Edges = []
    ne=0  #edge counter
    with open(follower_graph_filename) as fp:
        for cnt, line in enumerate(fp):
            line = line.strip('\n')
            users =line.split(",")
            follower = users[0]
            if follower in G.nodes():
                followings = users[1:]  #followings is a list of the people the follower follows
                for following in followings:
                    if following in G.nodes():
                        ne+=1
                        rate = G.nodes[following]['Rate']
                        G.add_edge(following,follower,Rate=rate)   #edge points from the following to the follower - edge shows flow of tweets
    return G

#Calculate the final opinions of the non stubborn nodes, and return a new updated Graph object (for drawing purposes)
def final_opinions(Ginitial):
    G = Ginitial.copy()  #we will add in the final opinions to this network object
    print("\tCalculating G,F,Psi matrices")
    (Gmat,Fmat,Psi)= graph_to_GFPsi(G);  #create the matrices we need for the opinion calculation.
    #print("G = %s matrix\nF = %s matrix\nPsi = %s vector"%(Gmat.shape,Fmat.shape,Psi.shape))
    b = Fmat @ Psi;  #b = Fmat*Psi, just makes notation cleaner for later functions
    print("\tSolving for opinions")

    opinion_nonstubborn = sparse.linalg.bicgstab(Gmat,b)[0];  #solve linear system to get non-stubborn opinions
    cnonstub=0
    #now we update the final opinons in G
    for node in G.nodes(data=True):
        if node[1]['Stubborn']==0:
            G.nodes[node[0]]['FinalOpinion'] = opinion_nonstubborn[cnonstub]
            if opinion_nonstubborn[cnonstub]>1:
                print("%s has opinion %s - not between 0 and 1"%(node,opinion_nonstubborn[cnonstub]))
            cnonstub+=1
    FinalOpinions = [ x[1]['FinalOpinion'] for x in G.nodes(data=True)]  #create a FinalOpinions list
    return (np.asarray(FinalOpinions),G)   #return the Final opinions as an array and also return the update graph object

#function to create Gmat,Fmat,Psi matrices and vectors for equilibrium calculation
def graph_to_GFPsi(G):
    n = int(len(G.nodes()))
    n_stubborn = int(sum([node[1]['Stubborn'] for node in G.nodes(data=True)]))
    n_nonstubborn = n-n_stubborn
    #Gmat = np.zeros((n_nonstubborn,n_nonstubborn))
    #Fmat= np.zeros((n_nonstubborn,n_stubborn))


    Psi = np.zeros((n_stubborn,1))
    G_Gmat ={}  #dictionary: key= node name, value = index in Gmat
    Gmat_G = {} #dictionary: key = index in Gmat, value = node name
    G_Fmat ={}  #dictionary: key = node name, value = index in Fmat and Psi
    Fmat_G = {} #dictionary: key = index in Fmat and Psi, value = node name
    data_G = []
    row_G = []
    col_G = []
    data_F = []
    row_F = []
    col_F = []
    #make dictionaries where I can look up the index of node in Gmat or Fmat.
    cstub=0
    cnonstub=0
    for node in G.nodes(data=True):
        name = node[1]['Name']
        opinion = node[1]['InitialOpinion']
        if node[1]['Stubborn']==1:
            Fmat_G[cstub]=name
            G_Fmat[name]=cstub
            Psi[cstub] = opinion
            cstub+=1
        elif node[1]['Stubborn']==0:
            G_Gmat[name] = cnonstub
            Gmat_G[cnonstub]=name
            cnonstub+=1

    #Calculate diagonal elements of Gmat
    for ind in range(cnonstub):
        node = Gmat_G[ind]
        w=0
        for nb in G.predecessors(node):
                w+=G.nodes[nb]['Rate']
        row_G.append(ind)
        col_G.append(ind)
        data_G.append(w)
        #Gmat[ind,ind] = w  #positive sign here


    #calculate off-diagonal elements of Gmat and Fmat
    for edge in G.edges(data=True):
        #print(edge)
        following = edge[0]
        follower = edge[1]
        rate = G.nodes[following]['Rate']  #rate of following.
        following_stub = G.nodes[following]['Stubborn']
        follower_stub = G.nodes[follower]['Stubborn']
        #print(follower,follower_stub,following,following_stub)
        if follower_stub==0 and following_stub==0:  #add an edge to Gmat because both non-stubborn
            i_follower = G_Gmat[follower]
            i_following = G_Gmat[following]
            #Gmat[i_follower,i_following]= -rate  #negative sign here
            row_G.append(i_follower)
            col_G.append(i_following)
            data_G.append(-rate)
        elif follower_stub==0 and following_stub==1:
            i_follower = G_Gmat[follower]
            i_following = G_Fmat[following]
            #Fmat[i_follower,i_following]= rate  #this sign is the opposite of Gmat
            row_F.append(i_follower)
            col_F.append(i_following)
            data_F.append(rate)
    Gmat = sparse.csr_matrix((data_G, (row_G, col_G)), shape=(n_nonstubborn, n_nonstubborn))
    Fmat = sparse.csr_matrix((data_F, (row_F, col_F)), shape=(n_nonstubborn,n_stubborn))
    return(Gmat,Fmat,Psi)

#calculate the risk index from a networkx object with opinions, stubborn, and bots
def risk_index(Gbot0):
	Gnobot = Gbot0.subgraph([x for x in Gbot0.nodes if Gbot0.nodes[x]["Bot"]==0])
	print("Solving for opinions with bots")
	(X,Gbot) = final_opinions(Gbot0)
	print("Solving for opinions without bots")
	(X,Gnobot) = final_opinions(Gnobot)
	OpinionsBot =[]
	OpinionsNoBot =[]
	print("Saving opinions to arrays")
	for node in Gbot.nodes():
		if Gbot.nodes[node]["Bot"]==0:
			opinion_nobot = Gnobot.nodes[node]['FinalOpinion']
			opinion_bot = Gbot.nodes[node]['FinalOpinion']
		else:
			opinion_nobot = Gbot.nodes[node]['FinalOpinion']
			opinion_bot = Gbot.nodes[node]['FinalOpinion']
		OpinionsBot.append(opinion_bot)
		OpinionsNoBot.append(opinion_nobot)
	OpinionsBot =np.asarray(OpinionsBot)
	OpinionsNoBot =np.asarray(OpinionsNoBot)
	ri = np.mean(OpinionsBot-OpinionsNoBot)
	return (ri,OpinionsNoBot,OpinionsBot,Gnobot,Gbot)

#find all nodes reachable by a stubborn user and return corresponding subgraph
def reachable_from_stubborn(G):
	ne = G.number_of_edges()
	nv = G.number_of_nodes()
	V={}  #keep track of all reachable nodes
	c = 0  #count how many nodes we iterate through
	cprint = 1e3  #how often to print status
	c_reach = 0  #count how many times we do reach calculation
	Stub =  [v for v in G.nodes if G.nodes[v]['Stubborn']==1]
	nstub = len(Stub)
	print("Checking reachable nodes from %s stubborn nodes"%nstub)
	for node in Stub:
		#print(node)

		if not(node in V):
			if (G.nodes[node]["Stubborn"]==1) or (G.nodes[node]["Bot"]==1):
				reach=nx.dfs_postorder_nodes(G, source=node, depth_limit=ne)
				V.update({i: 1 for i in [node]+list(reach)})
				#print("\t%s"%V)
				c_reach+=1
		c+=1
		if c%cprint==0: print("Node %s of %s, did reach check for %s nodes"%(c,nstub,c_reach))

    #V = list(set(V))
	print("Did reach check for only %s nodes out of %s"%(c_reach,nv))
	Gbot = G.subgraph(V)
	return (Gbot,V.keys())

def bot_neighbor_count(G):
	Vbot_followers=[]
	nbots = 0
	for node in G.nodes():
		if G.nodes[node]["Bot"]==1:
			nbots +=1
			nb = G.neighbors(node)
			Vbot_followers = Vbot_followers+[v for v in nb if G.nodes[v]["Bot"]==0]

	Vbot_followers = list(set(Vbot_followers))
	nbot_followers = len(Vbot_followers)

	return (nbot_followers,nbots,Vbot_followers)
