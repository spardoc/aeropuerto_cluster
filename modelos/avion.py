# modelos/avion.py
class Avion:
    def __init__(self, id, tipo, pasajeros):
        self.id = id
        self.tipo = tipo  # 'salida' o 'entrada'
        self.estado = 'en_puerta' if tipo == 'salida' else 'en_ruta'
        self.pasajeros = pasajeros
        self.posicion = (0, 0)

    def update_posicion(self, nueva_pos):
        self.posicion = nueva_pos

    def __str__(self):
        return f"Avion {self.id} - {self.tipo} - {self.estado}"