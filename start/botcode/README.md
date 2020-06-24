

# Bot Detection Code

- README for bot detector code-


What files in this repository:


	README_bot_code.txt
	The present readme

	MPI_graphCut.py
	The main file to run the bot detector

	networkClassifierHELPER.py
	The main Helper file for the bot detector

	ioHELPER.py
	Auxiliary input/output stream methods


## Introduction: what is the Bot Code for?

The code implements a bot detection method that classifies accounts as bots or humans, given the retweet graph of their interactions on a given event.

## What output to expect?

The code will create a folder named network_piBots_DB_NAME wher DB_NAME is the name of the database/event under study. This ‘keyword’ will be used in most paths to input/output files, so be consistent.

The folder will contain a CSV file with a name that looks like:

"ntwk_piBot_mu_1.0_alpha1_50.0_alpha2_500.0_lambda1_0.8_lambda2_0.6_epsilon_0.001_mode_normal_iteration_0_SEED_0.csv"

This is a CSV with two columns, the first one being the USER_ID, the second one the Bot score between 0 and 1 (0=human, 1=bot). Here is an example file produced:

Example:

    30408820; 0.42
    47186038; 0.51
    3082813560; 0.73
    762706392398467072; 0.5


## What input to feed the code?

First step

The first step is to collect a database, call it `DB_NAME`, of tweets and accounts on a given event (cf. search and stream files that create sqlite databases). Once this is done, one must construct the retweet graph and store it into a folder called `RT_graphs`, with path "/RT_graphs/DB_NAME_G0_RT_GRAPH.csv." This is a csv file with 3 columns:


    User1_ID (int)
    the user ID of a User1

    User2_ID (int)
    the user ID of a User2 (retweeted at least once by User1)

    Number of retweets (int) from User1 to User2


Example
If User1 with ID 12345 retweeted User2 with ID 54321 6 times, then there will be a line


    12345; 54321; 6;


In the csv file. Note that if User2 retweets User1 three (edit: six?) times; there will be another line


    54321; 12345; 6;


However, if User2 never retweeted User1, there will NOT be a line (edit: line with zero?):


    54321; 12345; 0;


Then, given that CSV, the code will produce a NetworkX object to apply efficient graph methods.

Once the Retweet Graph part is done, you must also specify hyperparameters to the classifier.






## Hyperparameters Inputs

To run the code, you must specify the following hyperparameters as arguments in the command line.


    mu (float)
    The value of the gamma parameter (cf. paper/thesis), usually I take gamma=1. In the code this parameter is called mu (in accordance with Chris Mark’s code)

    alpha1 (float)
    The value of the alpha1 parameter (cf. paper/thesis), usually I take alpha1=100, but this can vary (cf. paper/thesis)

    alpha2 (float)
    The value of the alpha2 parameter (cf. paper/thesis), usually I take alpha2=100, but this can vary (cf. paper/thesis)

    Iterations (int)
    The number of iterations (cuts): taken equal to 1 in paper experiments

    db (string)
    The database/event name to match folder paths: DB_NAME

    mode (string)
    The parameter “mode” describes which kind of prior one wants to use for node potentials. If no value specified, this will be a no prior (0.5 for all accounts).

    alambda1 (float)
    The value of the lambda11 parameter (cf. paper/thesis), called alambda1 in code. Usually I take alambda1=0.8.

    alambda2 (float)
    The value of the lambda00 parameter (cf. paper/thesis), called alambda2 in code. Usually I take alambda2=0.6.

    epsilon (float)
    the value the exponent such that the delta parameter (cf. paper/thesis) equals 10^-(epsilon). We want delta to be close to 0, so I usually take epsilon>=3.

    SEED (int)
    a random seed for sampling experiments


## Running the code

Before your run the code, make sure to install all required libraries, and get all helper scripts in the right folders.

### Pre-installing dependencies

Make sure to install the python libraries:
NetworkX (handles graphs, graph cut…)
MPI4py (handles MPI to parallelize on multiple processors)

### Run code from command line

Once you have navigated to the relevant folder, you can run the code with the following command:

```sh
python3 MPI_graphCut.py 1 100 100 1 YELLOW_VEST "normal" 0.8 0.6 3 0
```


Assuming you are working the Yellow Vest movement with (from left to right):

    mu=1
    Alpha1 = 100
    Alpha2 = 100
    Iteration = 1
    DB_NAME keyword (for retweets graph, and valid paths) called YELLOW_VEST
    Mode=’normal’ meaning no prior (every account at 0.5)
    Lambda11=0.8
    Lambda00=0.6
    Delta=10^(-3), hence lambda10=0.8+0.6-1+10^(-3)=0.401
    SEED=0


Finally, if you are running the code on a cluster to parallelize it on say 10 nodes, you want to add the `mpirun` command at the beginning of the command, where you specify the number of processor to parallelize on: here `np=10`

```sh
mpirun --oversubscribe -np 10 python3 MPI_graphCut.py 1 100 100 1 YELLOW_VEST "normal" 0.8 0.6 3 0
```
