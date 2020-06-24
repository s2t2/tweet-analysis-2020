



from mpi4py import MPI

class ClusterManager(object):
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



mgr = ClusterManager()









exit()

nproc = intracomm.Get_size() #> 1 in dev
rank  = intracomm.Get_rank() #> 0 in dev

print(rank != nproc - 1) #> (dev: False)
print(rank == nproc - 1) #> (dev: True)

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


# MPI.Finalize()
