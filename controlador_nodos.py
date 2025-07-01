# controlador_Nodos.py
from mpi4py import MPI
from multiprocessing import Process
import random
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    from Nodos.nodo_padre_gui import procesar_solicitud, iniciar_gui
    print("[Nodo 0] Maestro iniciado")
    iniciar_gui()

elif rank == 1:
    from Nodos.nodo_hijo_despego import procesar_vuelo_salida, PREFIJOS_SALIDA
    print("[Nodo 1] Vuelos salientes")
    vuelo_counter = 1
    while True:
        vuelo_id = f"{random.choice(PREFIJOS_SALIDA)}{vuelo_counter}"
        vuelo_counter += 1
        Process(target=procesar_vuelo_salida, args=(vuelo_id,)).start()
        time.sleep(15)

elif rank == 2:
    from Nodos.nodo_hijo_llegadas import simular_aterrizaje, PREFIJOS_LLEGADA
    print("[Nodo 2] Vuelos entrantes")
    vuelo_counter = 1
    while True:
        time.sleep(random.randint(20, 40))
        vuelo_id = f"{random.choice(PREFIJOS_LLEGADA)}{vuelo_counter}"
        vuelo_counter += 1
        vuelo = {
            "id": vuelo_id,
            "origen": random.choice(["Bogotá", "Miami", "Panamá", "Madrid"]),
            "destino": "Quito",
            "tipo": "entrada",
            "estado": "en_ruta",
            "pasajeros": 50
        }
        Process(target=simular_aterrizaje, args=(vuelo,)).start()