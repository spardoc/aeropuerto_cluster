from mpi4py import MPI
from multiprocessing import Process
import random
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    from Nodos.nodo_Padre_GUI import procesar_solicitud
    print("[Nodo 0] Nodo maestro iniciado")
    

elif rank == 1:
    from Nodos.nodo_Hijo_Despego import procesar_vuelo_salida, PREFIJOS_SALIDA
    print("[Nodo 1] Nodo vuelos salientes iniciado")
    
elif rank == 2:
    from Nodos.nodo_Hijo_Llegadas import simular_aterrizaje, PREFIJOS_LLEGADA
    print("[Nodo 2] Nodo vuelos entrantes iniciado")
    