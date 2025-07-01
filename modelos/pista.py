# modelos/pista.py
class Pista:
    def __init__(self):
        self.libre = True

    def ocupar(self):
        self.libre = False

    def liberar(self):
        self.libre = True