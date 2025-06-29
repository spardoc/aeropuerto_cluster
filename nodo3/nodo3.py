from mpi4py import MPI
import os
from multiprocessing import Process
import time
import random
import socket
import json

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

GUI_HOST = os.getenv("GUI_HOST", "192.168.100.100")

def enviar_evento(evento):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((GUI_HOST, 9999))
        s.send(json.dumps(evento).encode())
        s.close()
    except Exception as e:
        print(f"[Nodo {rank}] Error enviando evento: {e}")

def procesar_pasajero(pasajero_id, vuelo, puerta):
    print(f"[Nodo {rank}] Procesando pasajero {pasajero_id} del vuelo {vuelo} en puerta {puerta}")
    time.sleep(random.uniform(0.5, 1.5))  # Simula paso por seguridad/aduana
    print(f"[Nodo {rank}] Pasajero {pasajero_id} del vuelo {vuelo} completó el proceso")

def procesar_vuelo(vuelo, puerta):
    num_pasajeros = random.randint(3, 7)
    print(f"[Nodo {rank}] Recibido vuelo {vuelo} por puerta {puerta} con {num_pasajeros} pasajeros")

    # Enviar evento general
    enviar_evento({
        "tipo": "vuelo_aduana",
        "vuelo": vuelo,
        "puerta": puerta,
        "nodo": rank,
        "mensaje": f"Vuelo {vuelo} en aduana, puerta {puerta} con {num_pasajeros} pasajeros"
    })

    procesos = []
    for i in range(1, num_pasajeros + 1):
        p = Process(target=procesar_pasajero, args=(i, vuelo, puerta))
        p.start()
        procesos.append(p)

    for p in procesos:
        p.join()

    print(f"[Nodo {rank}] Todos los pasajeros del vuelo {vuelo} han sido procesados\n")

if __name__ == "__main__":
    if rank != 2:
        print(f"[Nodo {rank}] Este script es para nodo 3 (aduana). Saliendo...")
        exit(0)

    print(f"[Nodo {rank}] Nodo 3 (aduana y control de pasajeros) iniciado.")

    while True:
        vuelo, puerta = comm.recv(source=1, tag=88)
        print(f"[Nodo {rank}] Vuelo recibido desde nodo 2: {vuelo}, puerta {puerta}")

        # Procesar el vuelo en un proceso paralelo
        p = Process(target=procesar_vuelo, args=(vuelo, puerta))
        p.start()