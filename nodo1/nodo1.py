from mpi4py import MPI
from multiprocessing import Process
import os
import time
import random
import socket
import json

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

VUELOS = ["AAL123", "KLM455", "LATAM789", "IB318", "UA421"]

GUI_HOST = os.getenv("GUI_HOST", "192.168.100.100")

def enviar_evento(evento):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((GUI_HOST, 9999))
        s.send(json.dumps(evento).encode())
        s.close()
    except Exception as e:
        print(f"[Nodo {rank}] Error enviando evento: {e}")

def procesar_vuelo(vuelo):
    print(f"[Nodo {rank}] Aterrizando vuelo {vuelo}...")
    time.sleep(random.uniform(1.5, 3.0))  # Simula duración del proceso
    print(f"[Nodo {rank}] Vuelo {vuelo} aterrizado.")

    # Enviar evento a la GUI
    enviar_evento({
        "tipo": "vuelo_aterrizado",
        "vuelo": vuelo,
        "nodo": rank,
        "mensaje": f"Vuelo {vuelo} aterrizó"
    })

    # Enviar vuelo a nodo 1 (Puertas de embarque, rank=1)
    comm.send(vuelo, dest=1, tag=77)
    print(f"[Nodo {rank}] Vuelo {vuelo} enviado a nodo 1 (puertas).")

if __name__ == "__main__":
    if rank != 0:
        print(f"[Nodo {rank}] Este script es para la torre de control (rank 0). Saliendo...")
        exit(0)

    print(f"[Nodo {rank}] Torre de control iniciada.")

    while True:
        vuelo = random.choice(VUELOS)
        print(f"[Nodo {rank}] Vuelo entrante detectado: {vuelo}")
        p = Process(target=procesar_vuelo, args=(vuelo,))
        p.start()
        time.sleep(5)  # Simula intervalo entre vuelos
