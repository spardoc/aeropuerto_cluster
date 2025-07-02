from threading import Thread, Lock
import time
import random
from mpi4py import MPI
from modelos.avion import Avion  # Asegúrate de que sea reutilizable para llegadas

# --- MPI ---
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# --- Constantes ---
PREFIJOS_LLEGADA = ["AV", "UX", "EK", "CM"]
PUERTAS_IDS = ["Z1", "Z2", "Y1", "Y2", "X3", "X5"]
puertas = [{'id': pid, 'ocupada': False} for pid in PUERTAS_IDS]
lock = Lock()

# --- Flags de nodos existentes ---
TIENE_PADRE_LLEGADAS = size > 4
TIENE_GUI_SIMULACION = size > 5


def procesar_vuelo_llegada(avion):
    global puertas

    if TIENE_PADRE_LLEGADAS:
        comm.send(("estado_avion", {
            "id": avion.id,
            "estado": "esperando autorización"
        }), dest=4)
    time.sleep(3)

    print(f"[Llegada] Vuelo {avion.id} solicitando aterrizaje", flush=True)

    if TIENE_PADRE_LLEGADAS:
        comm.send(("solicitud_aterrizaje", {
            "id": avion.id,
            "pasajeros": avion.pasajeros
        }), dest=4)

    if TIENE_GUI_SIMULACION:
        comm.send(("solicitud_aterrizaje", {
            "id": avion.id,
            "pasajeros": avion.pasajeros
        }), dest=5)

    time.sleep(3)

    # 2. Esperar autorización
    while True:
        if TIENE_PADRE_LLEGADAS:
            try:
                if comm.Iprobe(source=4):
                    tipo, contenido = comm.recv(source=4)
                    if tipo == "autorizado_para_aterrizar" and contenido["id"] == avion.id:
                        print(f"[Llegada] Vuelo {avion.id} autorizado para aterrizar", flush=True)
                        break
            except MPI.Exception as e:
                print(f"[ERROR] Falló Iprobe/recv desde 4: {e}", flush=True)
        time.sleep(0.5)

    # 3. Buscar puerta disponible
    puerta_asignada = None
    while puerta_asignada is None:
        with lock:
            for puerta in puertas:
                if not puerta['ocupada']:
                    puerta['ocupada'] = True
                    puerta_asignada = puerta['id']
                    print(f"[Llegada] Vuelo {avion.id} asignado a puerta {puerta_asignada}", flush=True)

                    if TIENE_PADRE_LLEGADAS:
                        comm.send(("registro_llegada", {
                            "id": avion.id,
                            "puerta": puerta_asignada,
                            "pasajeros": avion.pasajeros,
                            "estado": "aterrizado"
                        }), dest=4)

                    if TIENE_GUI_SIMULACION:
                        comm.send(("registro_llegada", {
                            "id": avion.id,
                            "puerta": puerta_asignada,
                            "pasajeros": avion.pasajeros,
                            "estado": "aterrizado"
                        }), dest=5)

                    time.sleep(3)
                    break
        if puerta_asignada is None:
            print(f"[Rank {rank}] Vuelo {avion.id} esperando puerta libre...", flush=True)
            time.sleep(1)

    # 4. Aterrizando
    if TIENE_PADRE_LLEGADAS:
        comm.send(("estado_avion", {
            "id": avion.id,
            "estado": "aterrizando"
        }), dest=4)

    if TIENE_GUI_SIMULACION:
        comm.send(("estado_avion", {
            "id": avion.id,
            "estado": "aterrizando",
            "puerta": puerta_asignada
        }), dest=5)

    time.sleep(2)

    # 5. Desembarque
    if TIENE_PADRE_LLEGADAS:
        comm.send(("estado_avion", {
            "id": avion.id,
            "estado": "desembarcando"
        }), dest=4)

    if TIENE_GUI_SIMULACION:
        comm.send(("estado_avion", {
            "id": avion.id,
            "estado": "desembarcando",
            "puerta": puerta_asignada
        }), dest=5)

    while avion.pasajeros > 0:
        avion.pasajeros -= 1
        time.sleep(random.uniform(0.2, 0.7))

    # 6. Finalizado
    if TIENE_PADRE_LLEGADAS:
        comm.send(("estado_avion", {
            "id": avion.id,
            "estado": "finalizado"
        }), dest=4)

    if TIENE_GUI_SIMULACION:
        comm.send(("estado_avion", {
            "id": avion.id,
            "estado": "finalizado",
            "puerta": puerta_asignada
        }), dest=5)

    # 7. Liberar puerta
    with lock:
        for puerta in puertas:
            if puerta['id'] == puerta_asignada:
                puerta['ocupada'] = False
                print(f"[Llegada] Puerta {puerta_asignada} liberada por vuelo {avion.id}", flush=True)
                break


def lanzar_vuelos_continuamente():
    while True:
        avion = crear_avion_Llegada()
        t = Thread(target=procesar_vuelo_llegada, args=(avion,), daemon=True)
        t.start()
        time.sleep(random.uniform(1, 5))


def crear_avion_Llegada():
    vuelo_id = random.choice(PREFIJOS_LLEGADA) + str(random.randint(100, 999))
    pasajeros = random.randint(10, 50)
    return Avion(vuelo_id, "llegada", pasajeros)
