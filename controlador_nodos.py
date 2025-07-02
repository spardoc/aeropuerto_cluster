import os
from mpi4py import MPI
import sys

# Verificar si hay entorno gráfico disponible
if not os.environ.get("DISPLAY"):
    print("[GUI] ERROR: No se puede iniciar la interfaz, DISPLAY no está definido.")
    sys.exit(0)  # O return si estás dentro de una función

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

# Permitir asignar rank manualmente para ejecuciones fuera de mpiexec
if "MPI_RANK" in os.environ:
    rank = int(os.environ["MPI_RANK"])

print(f"[INFO] Ejecutando controlador con rank {rank}, tamaño total: {size}")

# Proteger cada bloque según tamaño del cluster
if rank == 0:
    from Nodos.nodo_padre_Vuelo_Salida import adminstrarVuelosEntrada
    print("[Nodo 0] Nodo maestro iniciado")
    adminstrarVuelosEntrada()

elif rank == 1:
    from Nodos.nodo_hijo_despego import lanzar_vuelos_continuamente
    print("[Nodo 1] Nodo vuelos salientes iniciado")
    lanzar_vuelos_continuamente()

elif rank == 2:
    if size > 2 or "MPI_RANK" in os.environ:
        from Nodos.interfaz_GUI_Tabla import iniciar_interfaz
        print("[Nodo 2] Interfaz GUI iniciada")
        iniciar_interfaz()
    else:
        print("[ERROR] Rank 2 no disponible en este contexto")

elif rank == 3:
    from Nodos.nodo_hijo_llegadas import lanzar_vuelos_continuamente
    print("[Nodo 3] Nodo administración de llegadas iniciado")
    lanzar_vuelos_continuamente()

elif rank == 4:
    if size > 4 or "MPI_RANK" in os.environ:
        from Nodos.nodo_padre_Vuelo_Llegada import adminstrarVuelosLlegando
        print("[Nodo 4] Nodo maestro de vuelos llegada")
        adminstrarVuelosLlegando()
    else:
        print("[ERROR] Rank 4 no disponible en este contexto")

elif rank == 5:
    if size > 5 or "MPI_RANK" in os.environ:
        from Nodos.simulacionGUI import iniciar_simulacion
        print("[Nodo 5] Nodo Simulacion")
        iniciar_simulacion()
    else:
        print("[ERROR] Rank 5 no disponible en este contexto")