import socket
import threading
import tkinter as tk
from PIL import Image, ImageTk
import json
import random

HOST = '0.0.0.0'
PORT = 9999

class gui:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Simulación Visual de Aeropuerto Animada")
        self.window.geometry("1000x600")

        self.canvas = tk.Canvas(self.window, bg="lightblue")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Escalar exactamente a 50x50 píxeles
        originalPlane = Image.open("images/plane.png")
        resized = originalPlane.resize((50, 50), Image.Resampling.LANCZOS)
        self.plane_img = ImageTk.PhotoImage(resized)

        originalGate = Image.open("images/gate.png")
        resized = originalGate.resize((50, 50), Image.Resampling.LANCZOS)
        self.gate_img = ImageTk.PhotoImage(resized)

        originalPassenger = Image.open("images/passenger.png")
        resized = originalPassenger.resize((50, 50), Image.Resampling.LANCZOS)
        self.passenger_img = ImageTk.PhotoImage(resized)

        # Textos de secciones
        self.canvas.create_text(500, 20, text="Torre de Control", font=("Arial", 16, "bold"))
        self.canvas.create_text(500, 220, text="Puertas de Embarque", font=("Arial", 16, "bold"))
        self.canvas.create_text(500, 420, text="Aduana", font=("Arial", 16, "bold"))

        # Diccionarios para rastrear elementos animados
        self.aviones = {}          # vuelo: { "id": canvas_id, "text_id": text_id, "x": pos_x, "target_x": target_x }
        self.vuelos_en_puerta = {} # vuelo: { "id": canvas_id, "text_id": text_id, "x": pos_x, "target_x": target_x }
        self.pasajeros = {}        # key: { "id": canvas_id, "text_id": text_id, "x": pos_x, "target_x": target_x }

        # Lock para sincronizar acceso
        self.lock = threading.Lock()

        # Iniciar servidor socket en hilo
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        server_thread.start()

        # Iniciar loop animación
        self.animar()

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            print("[GUI] Escuchando en puerto 9999...")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()

    def handle_client(self, conn):
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                try:
                    evento = json.loads(data.decode())
                    self.window.after(0, self.procesar_evento, evento)
                except json.JSONDecodeError:
                    print("[GUI] Error al decodificar JSON")

    def procesar_evento(self, evento):
        tipo = evento.get("tipo")
        vuelo = evento.get("vuelo")
        puerta = evento.get("puerta", "")

        with self.lock:
            if tipo == "vuelo_aterrizado":
                if vuelo not in self.aviones:
                    x, y = -50, 50
                    id_ = self.canvas.create_image(x, y, image=self.plane_img, anchor="nw")
                    text_id = self.canvas.create_text(x+20, y+40, text=vuelo, font=("Arial", 10))
                    self.aviones[vuelo] = {"id": id_, "text_id": text_id, "x": x, "y": y, "target_x": 200}

            elif tipo == "puerta_asignada":
                if vuelo not in self.vuelos_en_puerta:
                    x, y = -60, 250
                    id_ = self.canvas.create_image(x, y, image=self.gate_img, anchor="nw")
                    text_id = self.canvas.create_text(x+30, y+50, text=f"{vuelo} ({puerta})", font=("Arial", 9))
                    self.vuelos_en_puerta[vuelo] = {"id": id_, "text_id": text_id, "x": x, "y": y, "target_x": 700}

            elif tipo == "aduana":
                num = random.randint(3, 6)
                for i in range(num):
                    key = f"{vuelo}_{i}"
                    if key not in self.pasajeros:
                        x = -30 - i*30
                        y = 460 + random.randint(-10, 10)
                        id_ = self.canvas.create_image(x, y, image=self.passenger_img, anchor="nw")
                        text_id = self.canvas.create_text(x+10, y+40, text=str(i+1), font=("Arial", 8))
                        self.pasajeros[key] = {"id": id_, "text_id": text_id, "x": x, "y": y, "target_x": 500 + i*30}

    def animar(self):
        with self.lock:
            # Animar aviones en torre
            for vuelo, obj in list(self.aviones.items()):
                if obj["x"] < obj["target_x"]:
                    dx = min(5, obj["target_x"] - obj["x"])
                    self.canvas.move(obj["id"], dx, 0)
                    self.canvas.move(obj["text_id"], dx, 0)
                    obj["x"] += dx
                else:
                    # Llegó a destino, opcional: detener o eliminar
                    pass

            # Animar vuelos en puertas
            for vuelo, obj in list(self.vuelos_en_puerta.items()):
                if obj["x"] < obj["target_x"]:
                    dx = min(5, obj["target_x"] - obj["x"])
                    self.canvas.move(obj["id"], dx, 0)
                    self.canvas.move(obj["text_id"], dx, 0)
                    obj["x"] += dx
                else:
                    pass

            # Animar pasajeros en aduana
            for key, obj in list(self.pasajeros.items()):
                if obj["x"] < obj["target_x"]:
                    dx = min(3, obj["target_x"] - obj["x"])
                    self.canvas.move(obj["id"], dx, 0)
                    self.canvas.move(obj["text_id"], dx, 0)
                    obj["x"] += dx
                else:
                    pass

        # Repetir animación cada 50ms
        self.window.after(50, self.animar)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    gui = gui()
    gui.run()