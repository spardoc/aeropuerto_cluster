import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk
from mpi4py import MPI
import threading
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

ANCHO, ALTO = 1200, 800

# Coordenadas puertas de salida (superiores)
coordenadas_salida = {
    "A1": (460, 320),
    "A2": (500, 320),
    "B1": (540, 320),
    "B2": (580, 320),
    "C3": (620, 320),
    "C5": (660, 320)
}
coordenadas_llegada = {
    "Z1": (460, 560),
    "Z2": (500, 560),
    "Y1": (540, 560),
    "Y2": (580, 560),
    "X3": (620, 560),
    "X5": (660, 560)
}


ventana = tk.Tk()
ventana.title("Simulación Visual de Tráfico Aéreo (RANK 5)")
ventana.geometry(f"{ANCHO}x{ALTO}")
ventana.configure(bg="white")

canvas = Canvas(ventana, width=ANCHO-20, height=ALTO-20, bg="white")
canvas.pack(padx=10, pady=10)

# Imágenes
img_puerta = ImageTk.PhotoImage(Image.open("images/gate.png").resize((30, 30), Image.Resampling.LANCZOS))
img_pasajero = ImageTk.PhotoImage(Image.open("images/passenger.png").resize((20, 20), Image.Resampling.LANCZOS))
img_persona_desembarcando = ImageTk.PhotoImage(
    Image.open("images/person_walking.png").resize((20, 20), Image.Resampling.LANCZOS)
)
canvas.image_refs = [img_puerta, img_pasajero, img_persona_desembarcando]

# Estados visuales
estado_puertas_salida = {puerta: None for puerta in coordenadas_salida}
estado_puertas_llegada = {puerta: None for puerta in coordenadas_llegada}

def dibujar_puertas():
    canvas.delete("puerta")

    # --- Puertas de salida ---
    for puerta, (x, y) in coordenadas_salida.items():
        canvas.create_text(x + 15, y - 15, text=puerta, font=("Arial", 10, "bold"), tags="puerta", fill="black")
        canvas.create_image(x, y, anchor="nw", image=img_puerta, tags="puerta")

        if estado_puertas_salida.get(puerta) == "abordando":
            canvas.create_image(x + 5, y + 35, anchor="nw", image=img_pasajero, tags="puerta")

    # --- Puertas de llegada ---
    for puerta, (x, y) in coordenadas_llegada.items():
        canvas.create_text(x + 15, y - 15, text=puerta, font=("Arial", 10, "bold"), tags="puerta", fill="darkblue")
        canvas.create_image(x, y, anchor="nw", image=img_puerta, tags="puerta")

        if estado_puertas_llegada.get(puerta) == "desembarcando":
            canvas.create_image(x + 5, y + 35, anchor="nw", image=img_persona_desembarcando, tags="puerta")
            

    canvas.update()

def manejar_mensaje(tipo, contenido):
    if tipo == "estado_avion":
        puerta = contenido.get("puerta")
        estado = contenido.get("estado")

        if puerta in estado_puertas_salida:
            estado_puertas_salida[puerta] = "abordando" if estado == "abordando" else None
        elif puerta in estado_puertas_llegada:
            if estado == "desembarcando":
                estado_puertas_llegada[puerta] = "desembarcando"
            elif estado == "finalizado":
                estado_puertas_llegada[puerta] = None
            


        dibujar_puertas()

def recibir_mensajes():
    while True:
        if comm.Iprobe(source=MPI.ANY_SOURCE):
            msg = comm.recv()
            tipo, contenido = msg
            print(f"[SimulaciónGUI] Mensaje recibido: {tipo} -> {contenido}", flush=True)
            manejar_mensaje(tipo, contenido)
        time.sleep(0.01)

threading.Thread(target=recibir_mensajes, daemon=True).start()

def iniciar_simulacion():
    print(f"[SimulaciónGUI - Rank {rank}] Iniciada ventana de simulación", flush=True)
    dibujar_puertas()
    ventana.mainloop()
