



from mpi4py import MPI

node_name = MPI.Get_processor_name() # Node where this MPI process runs
print(node_name)

comm = MPI.COMM_WORLD
print(comm) #> <mpi4py.MPI.Intracomm object at 0x10ed94a70>

nproc = MPI.COMM_WORLD.Get_size() # Size of communicator (dev: 1)
rank  = MPI.COMM_WORLD.Get_rank() # Ranks in communicator (dev: 0)
print(rank != nproc - 1) #> (dev: False)
print(rank == nproc - 1) #> (dev: True)

breakpoint()





# MPI.Finalize()
