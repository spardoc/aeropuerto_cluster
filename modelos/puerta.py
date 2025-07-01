# modelos/puerta.py
class Puerta:
    def __init__(self, id):
        self.id = id
        self.ocupada = False

    def ocupar(self):
        self.ocupada = True

    def liberar(self):
        self.ocupada = False