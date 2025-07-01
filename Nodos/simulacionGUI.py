import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk
from mpi4py import MPI
import threading
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

ANCHO, ALTO = 1000, 800

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
# Lista de aviones actualmente en pista
aviones_en_pista = []
aviones_llegando = []

ventana = tk.Tk()
ventana.title("Simulación Visual de Tráfico Aéreo (RANK 5)")
ventana.geometry(f"{ANCHO}x{ALTO}")
ventana.configure(bg="white")

canvas = Canvas(ventana, width=ANCHO-20, height=ALTO-20, bg="white")
canvas.pack(padx=10, pady=10)

# Fondo
img_fondo = Image.open("images/aero.png").resize((ANCHO-20, ALTO-20), Image.Resampling.LANCZOS)
img_fondo_tk = ImageTk.PhotoImage(img_fondo)
canvas.create_image(0, 0, anchor="nw", image=img_fondo_tk)
canvas.image_refs = [img_fondo_tk]  # Inicializa la lista con la imagen de fondo

# Imágenes
img_puerta = ImageTk.PhotoImage(Image.open("images/gate.png").resize((30, 30), Image.Resampling.LANCZOS))
img_pasajero = ImageTk.PhotoImage(Image.open("images/passenger.png").resize((20, 30), Image.Resampling.LANCZOS))
img_persona_desembarcando = ImageTk.PhotoImage(Image.open("images/person_walking.png").resize((20, 20), Image.Resampling.LANCZOS))
img_terminal = ImageTk.PhotoImage(Image.open("images/terminal.png").resize((270, 150), Image.Resampling.LANCZOS))

img_airplane_flying = Image.open("images/airplane_flying.png").resize((30, 30), Image.Resampling.LANCZOS)
img_airplane_flying = img_airplane_flying.transpose(Image.FLIP_LEFT_RIGHT)
img_airplane_flying_tk = ImageTk.PhotoImage(img_airplane_flying)

img_airplane_gate = Image.open("images/airplane_gate.png").resize((30, 30), Image.Resampling.LANCZOS)
img_airplane_gate = img_airplane_gate.rotate(270, expand=True)  
img_airplane_gate_tk = ImageTk.PhotoImage(img_airplane_gate)

img_airplane_llegada = Image.open("images/airplane_llegada.png").resize((30, 30), Image.Resampling.LANCZOS)
img_airplane_llegada = img_airplane_llegada.rotate(270, expand=True)
img_airplane_llegada_tk = ImageTk.PhotoImage(img_airplane_llegada)

img_airplane_runway = Image.open("images/airplane_runway.png").resize((30, 30), Image.Resampling.LANCZOS)
img_airplane_runway = img_airplane_runway.transpose(Image.FLIP_LEFT_RIGHT)
img_airplane_runway_tk = ImageTk.PhotoImage(img_airplane_runway)

img_airplane_Llegada = ImageTk.PhotoImage(
    Image.open("images/airplane_gate.png").resize((30, 30), Image.Resampling.LANCZOS)
)

canvas.image_refs = [
    img_puerta, img_pasajero, img_persona_desembarcando,
    img_airplane_flying_tk, img_airplane_gate_tk, img_airplane_llegada_tk, img_airplane_runway_tk, img_airplane_Llegada
]


# Estados visuales
estado_puertas_salida = {puerta: None for puerta in coordenadas_salida}
estado_puertas_llegada = {puerta: None for puerta in coordenadas_llegada}

def dibujar_puertas():
    canvas.delete("puerta")

    # --- Puertas de salida ---
    for puerta, (x, y) in coordenadas_salida.items():
        if estado_puertas_salida.get(puerta) == "abordando":
            # Avión en puerta (arriba del texto)
            canvas.create_image(x , y - 60, anchor="nw", image=img_airplane_gate_tk, tags="puerta")

        # Texto de la puerta
        canvas.create_text(x + 15, y - 15, text=puerta, font=("Arial", 10, "bold"), tags="puerta", fill="black")
        
        # Imagen de la puerta
        canvas.create_image(x, y, anchor="nw", image=img_puerta, tags="puerta")

        # Pasajero debajo si abordando
        if estado_puertas_salida.get(puerta) == "abordando":
            canvas.create_image(x + 5, y + 35, anchor="nw", image=img_pasajero, tags="puerta")

    # --- Puertas de llegada ---
    for puerta, (x, y) in coordenadas_llegada.items():
        # Texto de puerta
        canvas.create_text(x + 15, y - 15, text=puerta, font=("Arial", 10, "bold"), tags="puerta", fill="darkblue")
        # Imagen de puerta
        canvas.create_image(x, y, anchor="nw", image=img_puerta, tags="puerta")

        if estado_puertas_llegada.get(puerta) == "desembarcando":

            canvas.create_image(x, y + 60, anchor="nw", image=img_airplane_Llegada, tags="puerta")

            canvas.create_image(x + 5, y + 35, anchor="nw", image=img_persona_desembarcando, tags="puerta")
            
    # --- Terminal ---
    x_terminal = ANCHO // 2 - 50
    y_terminal = 390
    canvas.create_image(x_terminal, y_terminal, anchor="nw", image=img_terminal, tags="puerta")

    canvas.update()

def dibujar_pista():
    canvas.delete("pista")
    for avion in aviones_en_pista:
        # Aumentar velocidad si despegando o en vuelo
        if avion["estado"] == "en pista":
            avion["x"] -= 4
            img = img_airplane_runway_tk
        elif avion["estado"] in ("despegando", "en vuelo"):
            avion["x"] -= 8
            img = img_airplane_flying_tk
        else:
            continue  # si el estado no es válido, lo ignoramos

        canvas.create_image(avion["x"], avion["y"], anchor="nw", image=img, tags="pista")
    canvas.update()

def animar_pista():
    while True:
        if aviones_en_pista:
            dibujar_pista()
            # Eliminar aviones que salieron del canvas
            aviones_en_pista[:] = [
                a for a in aviones_en_pista if a["x"] > -50
            ]
        time.sleep(0.03)

# Lanzar animación en hilo separado
threading.Thread(target=animar_pista, daemon=True).start()

def dibujar_llegadas():
    canvas.delete("llegada")
    for avion in aviones_llegando:
        avion["x"] += 8  # Movimiento de izquierda a derecha
        canvas.create_image(avion["x"], avion["y"], anchor="nw", image=img_airplane_llegada_tk, tags="llegada")
    canvas.update()

def animar_llegadas():
    while True:
        if aviones_llegando:
            dibujar_llegadas()
            # Eliminar si se sale del canvas por la derecha
            aviones_llegando[:] = [a for a in aviones_llegando if a["x"] < ANCHO + 100]
        time.sleep(0.03)

# Iniciar hilo de animación
threading.Thread(target=animar_llegadas, daemon=True).start()


def manejar_mensaje(tipo, contenido):
    if tipo == "estado_avion":
        id_avion = contenido.get("id")
        estado = contenido.get("estado")
        puerta = contenido.get("puerta")

        # Buscar avión en pista
        avion_existente = next((a for a in aviones_en_pista if a["id"] == id_avion), None)

        if estado == "en pista":
            if not avion_existente:
                aviones_en_pista.append({
                    "id": id_avion,
                    "x": ANCHO - 100,
                    "y": 50,
                    "estado": "en pista"
                })
        elif estado in ("despegando", "en vuelo"):
            if avion_existente:
                avion_existente["estado"] = estado
        else:
            # Estado ya no válido para animación => eliminar de la lista
            aviones_en_pista[:] = [a for a in aviones_en_pista if a["id"] != id_avion]
        avion_llegando = next((a for a in aviones_llegando if a["id"] == id_avion), None)

        if estado == "aterrizando":
            if not avion_llegando:
                aviones_llegando.append({
                    "id": id_avion,
                    "x": -50,
                    "y": 700,  # Ajusta según altura visual
                    "estado": "aterrizando"
                })
        elif estado in ("desembarcando", "finalizado"):
            aviones_llegando[:] = [a for a in aviones_llegando if a["id"] != id_avion]

        # Manejo de puertas
        if puerta in estado_puertas_salida:
            estado_puertas_salida[puerta] = "abordando" if estado == "abordando" else None
        elif puerta in estado_puertas_llegada:
            if estado == "desembarcando":
                estado_puertas_llegada[puerta] = "desembarcando"
                # Eliminar el avión de animación llegada si existe
                aviones_llegando[:] = [a for a in aviones_llegando if a["id"] != id_avion]
                # Marcar que debe dibujarse el avión estacionado en esa puerta
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
