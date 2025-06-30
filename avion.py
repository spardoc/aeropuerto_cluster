class Avion:
    def __init__(self, id_vuelo, origen, destino, tipo="salida"):
        self.id_vuelo = id_vuelo
        self.origen = origen
        self.destino = destino
        self.tipo = tipo  # "salida" o "entrada"
        self.estado = "en_gate" if tipo == "salida" else "en_ruta"  # o "aterrizando", "despegando"
        self.posiX = 0
        self.posiY = 0
        self.rotacion = 0
        self.pasajeros = 0 if tipo == "salida" else 50

    def embarcar_pasajero(self):
        if self.pasajeros < 50:
            self.pasajeros += 1

    def desembarcar_pasajero(self):
        if self.pasajeros > 0:
            self.pasajeros -= 1
