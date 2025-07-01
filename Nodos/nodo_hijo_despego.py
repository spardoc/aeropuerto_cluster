from threading import Thread
import time
from mpi4py import MPI
from multiprocessing import Lock, Manager, Process
import random
from modelos.avion import Avion

comm = MPI.COMM_WORLD
PREFIJOS_SALIDA = ["QF", "LA", "AA", "IB"]
PUERTAS_IDS = ["A1", "A2", "B1", "B2", "C3", "C5"]
puertas = [{'id': pid, 'ocupada': False} for pid in PUERTAS_IDS]
lock = Lock()

# Declarar que usaremos las variables globales puertas y lock
def procesar_vuelo_salida(avion):
    global puertas, lock

    puerta_asignada = None

    # Esperar hasta encontrar una puerta libre
    while puerta_asignada is None:
        with lock:
            for puerta in puertas:
                if not puerta['ocupada']:
                    puerta['ocupada'] = True
                    puerta_asignada = puerta['id']
                    print(f"[Salida] Vuelo {avion.id} asignado a puerta {puerta_asignada}" , flush=True)

                    # Notificar a administración
                    comm.send(("registro_salida", {
                        "id": avion.id,
                        "puerta": puerta_asignada,
                        "pasajeros": avion.pasajeros,
                        "estado": "en_puerta"
                    }), dest=0)
                    comm.send(("estado_avion", {
                        "id": avion.id,
                        "estado": "abordando",
                        "puerta": puerta_asignada  
                    }), dest=5)
                    break

        if puerta_asignada is None:
            print(f"[Rank {comm.Get_rank()}] Vuelo {avion.id} esperando puerta..." , flush=True)
            time.sleep(1)

    # Abordaje
    abordados = 0
    print(f"[Rank {comm.Get_rank()}] Vuelo {avion.id} abordando pasajeros ({avion.pasajeros} pasajeros)" , flush=True)

    comm.send(("estado_avion", {
        "id": avion.id,
        "estado": "abordando"
    }), dest=0)
    comm.send(("estado_avion", {
        "id": avion.id,
        "estado": "abordando"
    }), dest=5)
    while abordados < avion.pasajeros:
        nuevos = 1
        abordados += nuevos
        time.sleep(random.uniform(0.5, 1))

    # Abordaje finalizado
    print(f"[Rank {comm.Get_rank()}] Vuelo {avion.id} terminó de abordar", flush=True)

    print(f"[Rank {comm.Get_rank()}] Enviando estado 'en pista' para vuelo {avion.id} a rank 0", flush=True)
    comm.send(("estado_avion", {
        "id": avion.id,
        "estado": "en pista"
    }), dest=0)
    comm.send(("estado_avion", {
        "id": avion.id,
        "estado": "en pista"
    }), dest=5)
    
    # Liberar puerta
    with lock:
        for puerta in puertas:
            if puerta['id'] == puerta_asignada:
                puerta['ocupada'] = False
                print(f"[Salida] Puerta {puerta_asignada} liberada por vuelo {avion.id}", flush=True)
                break
    time.sleep(3)

    print(f"[Rank {comm.Get_rank()}] Waiting for takeoff authorization...", flush=True)
    msg = comm.recv(source=0)
    print(f"[Rank {comm.Get_rank()}] Message received: {msg}", flush=True)

    if msg[0] == "despegue_autorizado":
        print(f"[Rank {comm.Get_rank()}] Received takeoff authorization", flush=True)
        datos = msg[1]
        
        msg = ("estado_avion", {
            "id": avion.id,
            "estado": "despegando"
        })
        comm.send(msg, dest=0)
        comm.send(msg, dest=5)
        time.sleep(3)
        
        msg = ("estado_avion", {
            "id": avion.id,
            "estado": "en vuelo"
        })
        comm.send(msg, dest=0)
        comm.send(msg, dest=5)
        time.sleep(3)
        comm.send(("finalizado", avion.id), dest=0)


def lanzar_vuelos_continuamente():
    while True:
        avion = crear_avion_salida()
        t = Thread(target=procesar_vuelo_salida, args=(avion,), daemon=True)
        t.start()
        time.sleep(random.uniform(3, 8))


def crear_avion_salida():
    vuelo_id = random.choice(PREFIJOS_SALIDA) + str(random.randint(100, 999))
    pasajeros = random.randint(10, 50)
    return Avion(vuelo_id, "salida", pasajeros)
