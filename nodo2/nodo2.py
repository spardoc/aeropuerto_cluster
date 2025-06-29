from mpi4py import MPI
from multiprocessing import Process
import random
import time
import socket
import json
import os

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

# Lista de puertas disponibles
PUERTAS = ["A1", "A2", "B1", "B2", "C3", "C5"]

GUI_HOST = os.getenv("GUI_HOST", "192.168.100.100")

def enviar_evento(evento):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((GUI_HOST, 9999))
        s.send(json.dumps(evento).encode())
        s.close()
    except Exception as e:
        print(f"[Nodo {rank}] Error enviando evento: {e}")

def asignar_puerta(vuelo):
    puerta = random.choice(PUERTAS)
    print(f"[Nodo {rank}] Asignando puerta {puerta} al vuelo {vuelo}")
    time.sleep(random.uniform(1, 2.5))  # Simula tiempo de embarque
    print(f"[Nodo {rank}] Vuelo {vuelo} embarcado por puerta {puerta}")

    # Enviar evento a la GUI
    enviar_evento({
        "tipo": "puerta_asignada",
        "vuelo": vuelo,
        "puerta": puerta,
        "nodo": rank,
        "mensaje": f"Vuelo {vuelo} asignado a puerta {puerta}"
    })

    # Enviar vuelo al nodo 3 para simular proceso de aduana
    comm.send((vuelo, puerta), dest=2, tag=88)
    print(f"[Nodo {rank}] Vuelo {vuelo} enviado a nodo 3 para aduana.")

if __name__ == "__main__":
    if rank != 1:
        print(f"[Nodo {rank}] Este script es para nodo 2 (puertas de embarque). Saliendo...")
        exit(0)

    print(f"[Nodo {rank}] Nodo 2 (puertas) iniciado.")

    while True:
        # Esperar un vuelo desde nodo 1 (torre)
        vuelo = comm.recv(source=0, tag=77)
        print(f"[Nodo {rank}] Vuelo recibido: {vuelo}")

        # Procesar el vuelo en un subproceso
        p = Process(target=asignar_puerta, args=(vuelo,))
        p.start()
