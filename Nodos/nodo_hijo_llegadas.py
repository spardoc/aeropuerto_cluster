# Nodos/nodo_Hijo_Llegadas.py
import time
from mpi4py import MPI
import random

comm = MPI.COMM_WORLD
PREFIJOS_LLEGADA = ["AV", "UX", "EK", "CM"]

def simular_aterrizaje(vuelo):
    print(f"[Llegada] Vuelo {vuelo['id']} en ruta desde {vuelo['origen']}")
    comm.send(("solicitud_aterrizaje", vuelo["id"]), dest=0)
    tipo, puerta = comm.recv(source=0)
    if tipo == "aterrizaje_autorizado":
        print(f"[Llegada] Vuelo {vuelo['id']} aterrizó. Puerta asignada: {puerta}")
        time.sleep(5)
        print(f"[Llegada] Vuelo {vuelo['id']} descargando pasajeros")
        time.sleep(5)
        comm.send(("finalizado", vuelo["id"]), dest=0)