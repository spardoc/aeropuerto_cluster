import os
from mpi4py import MPI
import sys

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

print(f"Rank {rank} DISPLAY={os.environ.get('DISPLAY')}")

if "MPI_RANK" in os.environ:
    rank = int(os.environ["MPI_RANK"])

print(f"[INFO] Ejecutando controlador con rank {rank}, tamaño total: {size}")

if rank == 0:
    from Nodos.nodo_padre_Vuelo_Salida import adminstrarVuelosEntrada
    print("[Nodo 0] Nodo maestro iniciado")
    adminstrarVuelosEntrada()

elif rank == 1:
    from Nodos.nodo_hijo_despego import lanzar_vuelos_continuamente
    print("[Nodo 1] Nodo vuelos salientes iniciado")
    lanzar_vuelos_continuamente()

elif rank == 2:
    print("[Nodo 2] Omitido GUI Tabla para evitar problemas con DISPLAY")

elif rank == 3:
    from Nodos.nodo_hijo_llegadas import lanzar_vuelos_continuamente
    print("[Nodo 3] Nodo administración de llegadas iniciado")
    lanzar_vuelos_continuamente()

elif rank == 4:
    from Nodos.nodo_padre_Vuelo_Llegada import adminstrarVuelosLlegando
    print("[Nodo 4] Nodo maestro de vuelos llegada")
    adminstrarVuelosLlegando()

elif rank == 5:
    if os.environ.get("DISPLAY"):
        from Nodos.simulacionGUI import iniciar_simulacion
        print("[Nodo 5] Nodo Simulacion GUI iniciado")
        iniciar_simulacion()
    else:
        print("[Nodo 5] ERROR: DISPLAY no definido, no se puede iniciar GUI")