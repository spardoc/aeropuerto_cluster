import tkinter as tk
from tkinter import ttk
from mpi4py import MPI
import threading

comm = MPI.COMM_WORLD

ventana = tk.Tk()
ventana.title("Torre de Control - Estados de Vuelos (GUI RANK 4)")

# Diccionario para guardar estados: { vuelo_id: estado }
estados_aviones = {}
cola_despegue = []
lock_estados = threading.Lock()

# Separadores de vuelos
def es_vuelo_llegada(estado):
    return estado in ["esperando autorización", "aterrizando", "desembarcando", "finalizado"]

def es_vuelo_salida(estado):
    return estado in ["abordando", "en pista", "despegando", "en vuelo"]

# Pestañas
notebook = ttk.Notebook(ventana)
notebook.pack(expand=True, fill="both")

# Frame Salidas
frame_salidas = ttk.Frame(notebook)
notebook.add(frame_salidas, text="🛫 Salidas")
tabla_salidas = ttk.Treeview(frame_salidas, columns=("Vuelo", "Estado"), show="headings")
tabla_salidas.heading("Vuelo", text="Vuelo")
tabla_salidas.heading("Estado", text="Estado")
tabla_salidas.pack(expand=True, fill="both")

# Frame Llegadas
frame_llegadas = ttk.Frame(notebook)
notebook.add(frame_llegadas, text="🛬 Llegadas")
tabla_llegadas = ttk.Treeview(frame_llegadas, columns=("Vuelo", "Estado"), show="headings")
tabla_llegadas.heading("Vuelo", text="Vuelo")
tabla_llegadas.heading("Estado", text="Estado")
tabla_llegadas.pack(expand=True, fill="both")

def actualizar_tablas():
    with lock_estados:
        lista = list(estados_aviones.items())

    # Limpiar ambas tablas
    for row in tabla_salidas.get_children():
        tabla_salidas.delete(row)
    for row in tabla_llegadas.get_children():
        tabla_llegadas.delete(row)

    # Llenar tablas
    for vuelo_id, estado in lista:
        if es_vuelo_salida(estado):
            tabla_salidas.insert("", tk.END, values=(vuelo_id, estado))
        elif es_vuelo_llegada(estado):
            tabla_llegadas.insert("", tk.END, values=(vuelo_id, estado))

    ventana.after(1000, actualizar_tablas)

def recibir_mensajes():
    while True:
        if comm.Iprobe():
            msg = comm.recv()
            tipo, contenido = msg

            with lock_estados:
                if tipo == "estado_avion":
                    vuelo_id = contenido['id']
                    estado = contenido['estado']
                    estados_aviones[vuelo_id] = estado

                elif tipo == "actualizar_estados":
                    nuevos = contenido.get("aviones", {})
                    for vuelo_id, estado in nuevos.items():
                        estados_aviones[vuelo_id] = estado
                    cola_despegue[:] = contenido.get("cola", [])


                elif tipo == "registro_entrada":
                    print(f"[GUI] Registro de entrada recibido: {contenido}")

# Iniciar hilo de recepción y refresco
threading.Thread(target=recibir_mensajes, daemon=True).start()
actualizar_tablas()

ventana.mainloop()
