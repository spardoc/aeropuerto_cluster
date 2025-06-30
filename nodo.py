from mpi4py import MPI
import random
import time
import socket
import json
import os
import threading

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

# IP y puerto donde escucha la GUI
GUI_HOST = os.environ.get("GUI_HOST", "192.168.100.100")
GUI_PORT = 9999

VUELOS = ["AAL123", "KLM455", "LATAM789", "IB318", "UA421"]
PUERTAS = ["A1", "A2", "B1", "B2", "C3", "C5"]

def enviar_evento(evento):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((GUI_HOST, GUI_PORT))
        s.send(json.dumps(evento).encode())
        s.close()
    except Exception as e:
        print(f"[Nodo {rank}] Error enviando evento: {e}")

# Nodo 1: Torre de control (sin cambios)
if rank == 0:
    def procesar_vuelo(vuelo):
        print(f"[Nodo 1] Aterrizando vuelo {vuelo}...")
        time.sleep(random.uniform(1.5, 3.0))
        print(f"[Nodo 1] Vuelo {vuelo} aterrizado.")

        enviar_evento({
            "tipo": "vuelo_aterrizado",
            "vuelo": vuelo,
            "nodo": 1,
            "mensaje": f"Vuelo {vuelo} aterrizó"
        })

        # Enviar vuelo a nodo 2 (puertas)
        comm.send(vuelo, dest=1, tag=11)
        print(f"[Nodo 1] Vuelo {vuelo} enviado a puertas (nodo 2).")

    print("[Nodo 1] Torre iniciada.")
    while True:
        vuelo = random.choice(VUELOS)
        print(f"[Nodo 1] Vuelo entrante: {vuelo}")
        # Puedes seguir usando Process aquí o cambiar a threading si prefieres
        t = threading.Thread(target=procesar_vuelo, args=(vuelo,))
        t.start()
        time.sleep(5)

# Nodo 2: Puertas de embarque (usar hilos)
elif rank == 1:
    def asignar_puerta_y_reenviar(vuelo):
        puerta = random.choice(PUERTAS)
        print(f"[Nodo 2] Asignando puerta {puerta} al vuelo {vuelo}")
        time.sleep(random.uniform(1, 2.5))
        print(f"[Nodo 2] Vuelo {vuelo} embarcado por puerta {puerta}")

        enviar_evento({
            "tipo": "puerta_asignada",
            "vuelo": vuelo,
            "puerta": puerta,
            "nodo": 2,
            "mensaje": f"Vuelo {vuelo} asignado a puerta {puerta}"
        })

        # Enviar a nodo 3 (aduana)
        comm.send((vuelo, puerta), dest=2, tag=22)
        print(f"[Nodo 2] Vuelo {vuelo} enviado a aduana (nodo 3)")

    print("[Nodo 2] Puertas de embarque iniciadas.")
    while True:
        vuelo = comm.recv(source=0, tag=11)
        print(f"[Nodo 2] Vuelo recibido: {vuelo}")
        t = threading.Thread(target=asignar_puerta_y_reenviar, args=(vuelo,))
        t.start()

# Nodo 3: Aduana (usar hilos)
elif rank == 2:
    def procesar_pasajero(pasajero_id, vuelo, puerta):
        print(f"[Nodo 3] Procesando pasajero {pasajero_id} del vuelo {vuelo} en puerta {puerta}")
        time.sleep(random.uniform(0.5, 1.5))
        print(f"[Nodo 3] Pasajero {pasajero_id} del vuelo {vuelo} completó el proceso")

    def procesar_vuelo(vuelo, puerta):
        num_pasajeros = random.randint(3, 6)
        print(f"[Nodo 3] Recibido vuelo {vuelo} por puerta {puerta} con {num_pasajeros} pasajeros")

        enviar_evento({
            "tipo": "aduana",
            "vuelo": vuelo,
            "puerta": puerta,
            "nodo": 3,
            "mensaje": f"Vuelo {vuelo} procesando {num_pasajeros} pasajeros"
        })

        threads = []
        for i in range(num_pasajeros):
            t = threading.Thread(target=procesar_pasajero, args=(i + 1, vuelo, puerta))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        print(f"[Nodo 3] Todos los pasajeros del vuelo {vuelo} han sido procesados")

    print("[Nodo 3] Aduana iniciada.")
    while True:
        vuelo, puerta = comm.recv(source=1, tag=22)
        t = threading.Thread(target=procesar_vuelo, args=(vuelo, puerta))
        t.start()