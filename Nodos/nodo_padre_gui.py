import tkinter as tk
from modelos.avion import Avion
from mpi4py import MPI

comm = MPI.COMM_WORLD

# Estado del aeropuerto
vuelos_en_pista = {}
puertas_disponibles = ['A1', 'A2', 'B1', 'B2']
pista_libre = True

# GUI setup
ventana = tk.Tk()
ventana.title("Torre de Control")

canvas = tk.Canvas(ventana, width=800, height=400, bg="lightblue")
canvas.pack()

texto = tk.Text(ventana, height=10, width=100)
texto.pack()

# Diccionarios de seguimiento
aviones_gui = {}        # vuelo_id -> objeto gráfico en canvas
aviones_activos = {}    # vuelo_id -> instancia de Avion

# Utilidades
def log(msg):
    texto.insert(tk.END, msg + "\n")
    texto.see(tk.END)

def crear_avion_en_gui(avion):
    x, y = avion.posicion
    obj = canvas.create_oval(x, y, x+20, y+20, fill="red")
    aviones_gui[avion.id] = obj

def mover_avion_en_gui(avion_id, nueva_pos):
    if avion_id in aviones_gui:
        obj = aviones_gui[avion_id]
        x, y = nueva_pos
        canvas.coords(obj, x, y, x+20, y+20)

    if avion_id in aviones_activos:
        aviones_activos[avion_id].update_posicion(nueva_pos)

# Procesamiento de eventos
def procesar_solicitud(tipo, vuelo_id, source):
    global pista_libre

    if vuelo_id not in aviones_activos:
        avion = Avion(vuelo_id, tipo, 0)
        aviones_activos[vuelo_id] = avion
        crear_avion_en_gui(avion)

    if tipo == "despegue":
        if pista_libre:
            pista_libre = False
            log(f"Autorizando despegue: {vuelo_id}")
            comm.send(["despegue_autorizado", (10, 50)], dest=source)
            pista_libre = True
        else:
            log(f"Pista ocupada. {vuelo_id} esperando.")
    elif tipo == "aterrizaje":
        if pista_libre and puertas_disponibles:
            pista_libre = False
            puerta = puertas_disponibles.pop()
            log(f"Autorizando aterrizaje {vuelo_id} a puerta {puerta}")
            comm.send(["aterrizaje_autorizado", puerta], dest=source)
            pista_libre = True
        else:
            log(f"Pista o puertas ocupadas. {vuelo_id} esperando.")

def recibir():
    if comm.Iprobe():
        mensaje = comm.recv()
        tipo, contenido = mensaje

        if tipo == "solicitud_despegue":
            procesar_solicitud("despegue", contenido, 1)

        elif tipo == "solicitud_aterrizaje":
            procesar_solicitud("aterrizaje", contenido, 2)

        elif tipo == "finalizado":
            log(f"Vuelo {contenido} finalizado")
            if contenido in aviones_gui:
                canvas.delete(aviones_gui[contenido])
                del aviones_gui[contenido]
            if contenido in aviones_activos:
                del aviones_activos[contenido]

        elif tipo == "mover_avion":
            mover_avion_en_gui(contenido["id"], contenido["pos"])

    ventana.after(100, recibir)

def iniciar_gui():
    ventana.after(100, recibir)
    ventana.mainloop()