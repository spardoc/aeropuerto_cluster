from mpi4py import MPI
import threading
import time

comm = MPI.COMM_WORLD

# Recursos compartidos
cola_en_pista = []
cola_en_llegada = []
lock_cola = threading.Lock()
lock_estados = threading.Lock()
estados_aviones = {}
avion_a_rank = {}

def manejar_cola_despegues():
    while True:
        try:
            with lock_cola:
                current_queue = list(cola_en_pista)
            
            if current_queue:
                avion_id = current_queue[0]
                dest_rank = avion_a_rank.get(avion_id, 1)

                comm.send(("despegue_autorizado", {
                    "id": avion_id,
                    "coordenadas": (10, 50)
                }), dest=dest_rank)
                
                with lock_cola:
                    if cola_en_pista and cola_en_pista[0] == avion_id:
                        cola_en_pista.pop(0)

            time.sleep(0.5)
        except:
            time.sleep(1)


def adminstrarVuelosEntrada():
    threading.Thread(target=manejar_cola_despegues, daemon=True).start()

    while True:
        try:
            if comm.Iprobe(source=MPI.ANY_SOURCE):
                status = MPI.Status()
                msg = comm.recv(source=MPI.ANY_SOURCE, status=status)
                source_rank = status.Get_source()
                tipo, contenido = msg

                if tipo == "estado_avion":
                    avion_id = contenido['id']
                    estado = contenido['estado']
                    avion_a_rank[avion_id] = source_rank

                    with lock_estados:
                        estados_aviones[avion_id] = estado

                    if estado == "en pista":
                        with lock_cola:
                            if avion_id not in cola_en_pista:
                                cola_en_pista.append(avion_id)
                                print(f"[QUEUE] Agregado vuelo {avion_id} a la cola (total: {len(cola_en_pista)})", flush=True)

                    # 🔁 Enviar actualización a la GUI
                    with lock_estados, lock_cola:
                        if comm.Get_size() > 2:
                            comm.send(("actualizar_estados", {
                                "aviones": dict(estados_aviones),
                                "cola": list(cola_en_pista)
                            }), dest=2)

            time.sleep(0.01)
        except Exception as e:
            print(f"[ERROR] {e}", flush=True)
            time.sleep(1)
            
