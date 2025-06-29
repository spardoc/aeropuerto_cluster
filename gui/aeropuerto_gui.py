import tkinter as tk
import threading
import socket
import json

class AeropuertoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación Aeropuerto - GUI")
        self.canvas = tk.Canvas(root, width=900, height=600, bg="lightblue")
        self.canvas.pack()

        self.aviones = {}  # Dict: vuelo -> objeto gráfico (rectángulo)
        self.puertas = {}  # Dict: vuelo -> texto puerta
        self.pasajeros_procesados = 0

        # Etiqueta para mostrar resumen
        self.status_label = tk.Label(root, text="Eventos recibidos: 0")
        self.status_label.pack()

        self.event_count = 0

        # Inicia servidor en hilo aparte
        threading.Thread(target=self.socket_server, daemon=True).start()

    def socket_server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', 9999))
        s.listen(5)
        print("[GUI] Servidor TCP iniciado en puerto 9999")

        while True:
            conn, addr = s.accept()
            data = conn.recv(1024)
            if data:
                try:
                    evento = json.loads(data.decode())
                    self.root.after(0, self.procesar_evento, evento)
                except Exception as e:
                    print(f"[GUI] Error procesando evento: {e}")
            conn.close()

    def procesar_evento(self, evento):
        self.event_count += 1
        self.status_label.config(text=f"Eventos recibidos: {self.event_count}")

        tipo = evento.get("tipo")
        vuelo = evento.get("vuelo")
        nodo = evento.get("nodo")
        mensaje = evento.get("mensaje", "")

        print(f"[GUI] Evento: {tipo}, Vuelo: {vuelo}, Nodo: {nodo}, Mensaje: {mensaje}")

        if tipo == "vuelo_aterrizado":
            # Dibuja un avión como rectángulo a la izquierda, uno debajo del otro
            y = 50 + len(self.aviones)*40
            rect = self.canvas.create_rectangle(10, y, 110, y+30, fill="white", outline="black")
            text = self.canvas.create_text(60, y+15, text=vuelo)
            self.aviones[vuelo] = (rect, text)

        elif tipo == "puerta_asignada":
            # Dibuja la puerta asignada a la derecha del avión
            if vuelo in self.aviones:
                rect, text = self.aviones[vuelo]
                coords = self.canvas.coords(rect)
                y = coords[1]
                # Dibuja texto puerta a la derecha
                if vuelo in self.puertas:
                    self.canvas.delete(self.puertas[vuelo])
                puerta_text = self.canvas.create_text(200, y+15, text=evento.get("puerta"), fill="blue", font=("Arial", 12, "bold"))
                self.puertas[vuelo] = puerta_text

        elif tipo == "vuelo_aduana":
            # Marca que pasajeros están siendo procesados (simple cambio de color)
            if vuelo in self.aviones:
                rect, text = self.aviones[vuelo]
                self.canvas.itemconfig(rect, fill="lightgreen")

        # Puedes agregar más visualizaciones para otros tipos

if __name__ == "__main__":
    root = tk.Tk()
    app = AeropuertoGUI(root)
    root.mainloop()