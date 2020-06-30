

def parse_bidirectional_links(graph, weight_attr="rt_count"):
    """
    Computes the degree to which the users in each edge were retweeting eachother.

    Adapted from the "getLinkDataRestrained" function in the "networkClassifierHELPER" file.

    Params:
        graph (networkx.DiGraph) a retweet graph,
            with each edge like: ("user", "retweeted_user", rt_count=10)

    Returns:
        a list of links, each like: ['user1', 'leader1', True, False, 4.0, 0]
            where the first two values are the users,
            the third boolean indicates whether or not the first retweeted the second,
            the fourth boolean indicates whether or not the second retweeted the first,
            the fifth float indicates the strength or number of times the first user retweeted the second,
            the sixth float indicates the strength or number of times the second user retweeted the first

    TODO: prefer to return data in dictionary format, as long as the performance isn't affected
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

            link = [user, retweeted_user, True, has_reverse_edge, edge_weight, reverse_edge_weight]
            #> ['user1', 'leader1', True, False, 4.0, 0] # TODO: prefer to assemble a dict here, for more explicit access later
            links.append(link)
    return links



def compute_joint_energy(u1, u2, wlr, in_graph, out_graph, alpha, alambda1, alambda2, epsilon):
    """
    Computes joint energy potential between two users.

    Copied unchanged from the "psi" function in the "networkClassifierHELPER" file.

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
