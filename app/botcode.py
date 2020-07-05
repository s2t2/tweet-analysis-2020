
import os

from dotenv import load_dotenv
import numpy as np

from networkx import DiGraph, minimum_cut

# load_dotenv()

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

RANDOM_SEED = int(os.getenv("RANDOM_SEED", default="0"))
np.random.seed(RANDOM_SEED)

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

def compute_link_energy(u1, u2, rt_count, in_graph, out_graph, alpha=ALPHA, alambda1=LAMBDA_1, alambda2=LAMBDA_2, epsilon=EPSILON):
    """
    Computes joint energy potential between two users.

    Copied unchanged from the "psi" function in the "networkClassifierHELPER" file.

	Params:
        u1 (int or str) unique identifier for user 1
	    u2 (int or str) unique identifier for user 2
	    rt_count (int) number of retweets from u1 to u2
        out_graph (dict of ints) a graph that stores out degrees of accounts in retweet graph
        in_graph (dict of ints) a graph that stores in degrees of accounts in retweet graph

        alpha (list of floats) a list containing hyperparams mu, alpha1, alpha2
        alambda1 (float) value of lambda11
        alambda2 (float) value of lambda00
        epsilon (int) exponent such that delta=10^(-espilon), where lambda01=lambda11+lambda00-1+delta
	"""

    hyperparam_const = (alambda2 + alambda1 - 1 + epsilon) #> 0.4009999999999999

    # if user 1 is not retweeting or user2 is not getting retweeted...
    # ... expects user 1 to be retweeting
    # ... expects user 2 to be getting retweeted
    if out_graph[u1] == 0 or in_graph[u2] == 0:
        raise ValueError(f"Relationship problem: '{u1}' --> '{u2}'")

    #breakpoint()

    #here alpha is a vector of length three, psi decays according to a logistic sigmoid function
    val_00 = 0
    val_01 = 0
    val_10 = 0
    val_11 = 0

    temp_1 = alpha[1] / float(out_graph[u1]) - 1 #> 100 / 8 = 12.5
    temp_2 = alpha[2] / float(in_graph[u2]) - 1 #> 100 / 10 = 10.0
    temp =  temp_1 + temp_2
    print("TEMP", temp) #> 20.5

    # what would get the temp to be less than 10? rt_count sufficiently high (>20) relative to ALPHA vals (100)

    if temp < 10:
        # see: https://numpy.org/doc/stable/reference/generated/numpy.exp.html
        # np.exp(1) #> 2.718281828459045
        # np.exp(2) #> 7.38905609893065
        # np.exp(3) #> 20.085536923187668
        # np.exp(4) #> 54.598150033144236
        # np.exp(5) #> 148.4131591025766
        # np.exp(6) #> 403.4287934927351
        # np.exp(7) #> 1096.6331584284585
        # np.exp(8) #> 2980.9579870417283
        # np.exp(9) #> 8103.083927575384
        # np.exp(10) #> 22026.465794806718
        val_01 = rt_count * alpha[0] / (1 + np.exp(temp))
    else:
        val_01 = 0
    print("VAL:", val_01) #> 0



    # all these depend on val_01, and if it is zero so are they
    val_10 = hyperparam_const * val_01
    val_00 = alambda2 * val_01
    val_11 = alambda1 * val_01

    test2 = 0.5 * val_11 + 0.25 * (val_10 - val_01)
    test3 = 0.5 * val_00 + 0.25 * (val_10 - val_01)
    if(min(test2, test3) < 0):
        print("DETECTED / FIXING NEGATIVE EDGE")
        val_00 = val_11 = 0.5 * val_01

    if(val_00 + val_11 > val_01 + val_10):
        print(u1, u2)
        print('psi_01', val_01)
        print('psi_11', val_11)
        print('psi_00', val_00)
        print('psi_10', val_10)
        print("\n")

    return [val_00, val_01, val_10, val_11]

def compile_energy_graph(G, piBot, edgelist_data, graph_out, graph_in):
    """
    Takes as input the RT graph and builds the energy graph.

    Then cuts the energy graph to classify.

	Params:

	    G (ntwkX graph)
		    the Retweet Graph from buildRTGraph

        piBot (dict of floats)
		    a dictionnary with prior on bot probabilities.
            Keys are users_ids, values are prior bot scores.

        edgelist_data (list of  tuples)
		    information about edges to build energy graph.
		    This list comes in part from the getLinkDataRestrained method

        graph_out (dict of ints)
		    a graph that stores out degrees of accounts in retweet graph

        graph_in (dict of ints)
		    a graph that stores in degrees of accounts in retweet graph

	"""
    H = DiGraph()
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

    cut_value, mc = minimum_cut(H,1,0)
    PL = list(mc[0]) #the other way around
    if 1 not in PL:
        print("Double check")
        PL = list(mc[1])
    PL.remove(1)

    return H, PL, user_data
