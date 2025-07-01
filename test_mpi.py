from mpi4py import MPI
import socket

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
hostname = socket.gethostname()

print(f"Este es el rank {rank} de {comm.Get_size()} ejecutándose en {hostname}")

if rank == 0:
    data = {"message": "Hola desde el rank 0!"}
else:
    data = None

data = comm.bcast(data, root=0)
print(f"Rank {rank} recibió:", data["message"])