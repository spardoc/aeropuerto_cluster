from mpi4py import MPI
from threading import Thread
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    from Nodos.nodo_padre_Vuelo_Salida import adminstrarVuelosEntrada
    print("[Nodo 0] Nodo maestro iniciado")
    
    adminstrarVuelosEntrada()

elif rank == 1:
    from Nodos.nodo_hijo_despego import lanzar_vuelos_continuamente
    print("[Nodo 1] Nodo vuelos salientes iniciado")
    lanzar_vuelos_continuamente()

elif rank == 2:
    from Nodos.interfaz_GUI_Tabla import iniciar_interfaz
    print("[Nodo 2] Interfaz GUI iniciada")
    iniciar_interfaz()

elif rank == 3:
    from Nodos.nodo_hijo_llegadas import lanzar_vuelos_continuamente
    print("[Nodo 3] Nodo administración de llegadas iniciado")
    lanzar_vuelos_continuamente()

elif rank == 4:
    from Nodos.nodo_padre_Vuelo_Llegada import adminstrarVuelosLlegando
    print("[Nodo 4] Nodo maestro de vuelos llegada")
    
    adminstrarVuelosLlegando()

elif rank == 5:
    from Nodos.simulacionGUI import iniciar_simulacion
    print("[Nodo 5] Nodo Simulacion")
    iniciar_simulacion()


