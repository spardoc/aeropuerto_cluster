from mpi4py import MPI
import os
import time
import socket
import json

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

GUI_HOST = os.getenv("GUI_HOST", "192.168.100.100")

# Estado de la pista: None, "despegue", "aterrizaje"
estado_pista = None
pista_ocupada = False
cola_espera = []

def enviar_evento(evento):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((GUI_HOST, 9999))
        s.send(json.dumps(evento).encode())
        s.close()
    except Exception as e:
        print(f"[Nodo {rank}] Error enviando evento: {e}")

def procesar_solicitud(tipo, vuelo_id, source):
    global pista_ocupada, estado_pista

    if not pista_ocupada:
        pista_ocupada = True
        estado_pista = tipo

        enviar_evento({
            "tipo": f"{tipo}_autorizado",
            "vuelo": vuelo_id,
            "mensaje": f"Vuelo {vuelo_id} autorizado para {tipo}"
        })

        comm.send("autorizado", dest=source)
        simular_movimiento_en_pista(vuelo_id, tipo)

        pista_ocupada = False
        estado_pista = None

        # Si hay vuelos en espera, podrías liberarlos aquí (extra)
    else:
        enviar_evento({
            "tipo": f"{tipo}_rechazado",
            "vuelo": vuelo_id,
            "mensaje": f"Pista ocupada. Vuelo {vuelo_id} no puede {tipo} aún."
        })

        comm.send("rechazado", dest=source)

def simular_movimiento_en_pista(vuelo_id, tipo):
    enviar_evento({
        "tipo": "movimiento",
        "vuelo": vuelo_id,
        "posiX": 0,
        "posiY": 0,
        "mensaje": f"Vuelo {vuelo_id} en movimiento por pista para {tipo}"
    })
    for paso in range(1, 6):
        time.sleep(0.5)
        enviar_evento({
            "tipo": "movimiento",
            "vuelo": vuelo_id,
            "posiX": paso * 20,
            "posiY": 100 if tipo == "despegue" else 200,
        })

    enviar_evento({
        "tipo": f"{tipo}_completo",
        "vuelo": vuelo_id,
        "mensaje": f"Vuelo {vuelo_id} completó el {tipo}"
    })
