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

GUI_HOST = os.getenv("GUI_HOST", "192.168.100.100")
PREFIJOS = ["AAL", "KLM", "LATAM", "IB", "UA"]

def enviar_evento(evento):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((GUI_HOST, 9999))
        s.send(json.dumps(evento).encode())
        s.close()
    except Exception as e:
        print(f"[Nodo {rank}] Error enviando evento: {e}")

def simular_embarque(vuelo):
    pasajeros = 0
    while pasajeros < 50:
        time.sleep(0.2)
        pasajeros += 1
        if pasajeros % 10 == 0:
            enviar_evento({
                "tipo": "embarque_parcial",
                "vuelo": vuelo["id"],
                "pasajeros": pasajeros,
                "mensaje": f"Vuelo {vuelo['id']} embarcando ({pasajeros}/50)"
            })
    vuelo["pasajeros"] = pasajeros
    vuelo["estado"] = "en_pista"
    vuelo["puerta"] = random.choice(["A1", "A2", "B1", "C3", "D4", "E5"])
    enviar_evento({
        "tipo": "puerta_asignada",
        "vuelo": vuelo["id"],
        "puerta": vuelo["puerta"],
        "mensaje": f"Puerta de embarque asignada: {vuelo['puerta']}"
    })

def solicitar_despegue_y_esperar(vuelo):
    vuelo["estado"] = "despegando"
    comm.send(("solicitud_despegue", vuelo["id"]), dest=0)
    enviar_evento({
        "tipo": "solicitud_despegue",
        "vuelo": vuelo["id"],
        "mensaje": f"Vuelo {vuelo['id']} solicitó permiso de despegue"
    })

    permiso = comm.recv(source=0)
    if permiso == "autorizado":
        enviar_evento({
            "tipo": "despegue_autorizado",
            "vuelo": vuelo["id"],
            "mensaje": f"Vuelo {vuelo['id']} autorizado a despegar"
        })
    else:
        enviar_evento({
            "tipo": "despegue_rechazado",
            "vuelo": vuelo["id"],
            "mensaje": f"Vuelo {vuelo['id']} debe esperar para despegar"
        })

def procesar_vuelo_salida(vuelo_id):
    vuelo = {
        "id": vuelo_id,
        "origen": "Quito",
        "destino": random.choice(["Madrid", "NYC", "Bogotá"]),
        "estado": "en_gate",
        "pasajeros": 0,
        "tipo": "salida"
    }

    enviar_evento({
        "tipo": "vuelo_creado",
        "vuelo": vuelo["id"],
        "mensaje": f"Vuelo {vuelo['id']} creado para salida"
    })

    simular_embarque(vuelo)
    solicitar_despegue_y_esperar(vuelo)
