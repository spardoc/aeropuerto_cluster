from mpi4py import MPI
import threading
import time

comm = MPI.COMM_WORLD
gui_rank = 2  # GUI ahora en el proceso rank 2

# Recursos compartidos
cola_en_llegada = []
lock_cola = threading.Lock()
lock_estados = threading.Lock()
estados_aviones = {}
avion_a_rank = {}

def manejar_cola_llegadas():
    while True:
        try:
            with lock_cola:
                current_queue = list(cola_en_llegada)
            
            if current_queue:
                avion_id = current_queue[0]
                dest_rank = avion_a_rank.get(avion_id, 4)

                comm.send(("autorizado_para_aterrizar", {
                    "id": avion_id,
                    "coordenadas": (10, 50)
                }), dest=dest_rank)
                
                with lock_cola:
                    if cola_en_llegada and cola_en_llegada[0] == avion_id:
                        cola_en_llegada.pop(0)

            time.sleep(0.5)
        except:
            time.sleep(1)
     
def adminstrarVuelosLlegando():
    while True:
        try:
            if comm.Iprobe(source=MPI.ANY_SOURCE):
                status = MPI.Status()
                msg = comm.recv(source=MPI.ANY_SOURCE, status=status)
                source_rank = status.Get_source()
                tipo, contenido = msg

                if tipo == "solicitud_aterrizaje":
                    avion_id = contenido['id']
                    print(f"[LLEGADA] Solicitud de aterrizaje para vuelo {avion_id} desde rank {source_rank}", flush=True)

                    # Puedes añadir lógica más compleja si quieres validar antes de autorizar
                    comm.send(("autorizado_para_aterrizar", {
                        "id": avion_id
                    }), dest=source_rank)

                elif tipo == "estado_avion":
                    avion_id = contenido['id']
                    estado = contenido['estado']
                    avion_a_rank[avion_id] = source_rank

                    with lock_estados:
                        estados_aviones[avion_id] = estado

                    # 🔁 Enviar actualización a la GUI
                    with lock_estados, lock_cola:
                        comm.send(("actualizar_estados", {
                            "aviones": dict(estados_aviones),
                            "cola": list(cola_en_llegada)
                        }), dest=gui_rank)  

            time.sleep(0.01)

        except Exception as e:
            print(f"[ERROR - Llegadas] {e}", flush=True)
            time.sleep(1)
