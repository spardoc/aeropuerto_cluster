from mpi4py import MPI
from multiprocessing import Process
import random
import time
import socket
import json
import os

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

GUI_HOST = os.getenv("GUI_HOST", "192.168.100.100")
PUERTAS_LLEGADA = ["F1", "F2", "G1", "G2", "H3", "J5"]
PREFIJOS_LLEGADA = ["LATAMS", "UAS", "IBS", "KLMN", "AALS"]

def enviar_evento(evento):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((GUI_HOST, 9999))
        s.send(json.dumps(evento).encode())
        s.close()
    except Exception as e:
        print(f"[Nodo {rank}] Error enviando evento: {e}")

def simular_aterrizaje(vuelo):
    enviar_evento({
        "tipo": "vuelo_en_ruta",
        "vuelo": vuelo["id"],
        "mensaje": f"Vuelo {vuelo['id']} aproximándose al aeropuerto"
    })

    # Pedir permiso a Nodo 0
    comm.send(("solicitud_aterrizaje", vuelo["id"]), dest=0)
    respuesta = comm.recv(source=0)

    if respuesta != "autorizado":
        enviar_evento({
            "tipo": "esperando_aterrizaje",
            "vuelo": vuelo["id"],
            "mensaje": f"Vuelo {vuelo['id']} esperando para aterrizar"
        })
        while respuesta != "autorizado":
            time.sleep(3)
            comm.send(("solicitud_aterrizaje", vuelo["id"]), dest=0)
            respuesta = comm.recv(source=0)

    vuelo["estado"] = "aterrizando"
    enviar_evento({
        "tipo": "aterrizando",
        "vuelo": vuelo["id"],
        "mensaje": f"Vuelo {vuelo['id']} aterrizando"
    })
    time.sleep(random.uniform(1.5, 3.0))

    vuelo["estado"] = "aterrizado"
    puerta = random.choice(PUERTAS_LLEGADA)
    vuelo["puerta"] = puerta
    enviar_evento({
        "tipo": "aterrizado",
        "vuelo": vuelo["id"],
        "puerta": puerta,
        "mensaje": f"Vuelo {vuelo['id']} aterrizó en puerta {puerta}"
    })

    # Simular desembarque
    while vuelo["pasajeros"] > 0:
        time.sleep(0.2)
        vuelo["pasajeros"] -= 1
        if vuelo["pasajeros"] % 10 == 0:
            enviar_evento({
                "tipo": "desembarque_parcial",
                "vuelo": vuelo["id"],
                "pasajeros_restantes": vuelo["pasajeros"],
                "mensaje": f"{vuelo['pasajeros']} pasajeros aún desembarcando en vuelo {vuelo['id']}"
            })

    enviar_evento({
        "tipo": "desembarque_completo",
        "vuelo": vuelo["id"],
        "mensaje": f"Pasajeros del vuelo {vuelo['id']} desembarcados"
    })
