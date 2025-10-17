from abc import ABC, abstractmethod
from models.ejercicios import EJERCICIOS

class ObjetivoBase(ABC):
    @abstractmethod
    def obtener_ejercicios(self):
        pass

class BajarPeso(ObjetivoBase):
    def obtener_ejercicios(self):
        return EJERCICIOS["bajar_peso"]

class GanarVolumen(ObjetivoBase):
    def obtener_ejercicios(self):
        return EJERCICIOS["volumen"]

class DefinicionMuscular(ObjetivoBase):
    def obtener_ejercicios(self):
        return EJERCICIOS["definicion"]

class Tonificar(ObjetivoBase):
    def obtener_ejercicios(self):
        return EJERCICIOS["tonificar"]

class Flexibilidad(ObjetivoBase):
    def obtener_ejercicios(self):
        return EJERCICIOS["flexibilidad"]
