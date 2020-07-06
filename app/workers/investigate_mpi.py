


import os
from pprint import pprint

from mpi4py import MPI
import numpy as np
from networkx import DiGraph

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


if __name__ == "__main__":

    manager = ClusterManager()
