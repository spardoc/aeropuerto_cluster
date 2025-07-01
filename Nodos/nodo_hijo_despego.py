# Nodos/nodo_hijo_despego.py
import time
import random
from mpi4py import MPI

comm = MPI.COMM_WORLD
PREFIJOS_SALIDA = ["QF", "LA", "AA", "IB"]

def procesar_vuelo_salida(vuelo_id):
    pasajeros_totales = random.randint(30, 80)
    abordados = 0
    print(f"[Salida] Vuelo {vuelo_id} abordando pasajeros ({pasajeros_totales} pasajeros)")
    while abordados < pasajeros_totales:
        nuevos = random.randint(3, 10)
        abordados += nuevos
        print(f"[Salida] Vuelo {vuelo_id} abordando... {abordados}/{pasajeros_totales}")
        time.sleep(random.uniform(0.3, 1.0))

    comm.send(("solicitud_despegue", vuelo_id), dest=0)
    tipo, datos = comm.recv(source=0)
    if tipo == "despegue_autorizado":
        print(f"[Salida] Vuelo {vuelo_id} despegando en coordenadas {datos}")

        # Simular movimiento enviando posiciones
        for x in range(10, 100, 10):
            pos = (x, 50)
            comm.send(("mover_avion", {"id": vuelo_id, "pos": pos}), dest=0)
            time.sleep(0.5)

        comm.send(("finalizado", vuelo_id), dest=0)