import json, os, random
from models.objetivos import BajarPeso, GanarVolumen, DefinicionMuscular, Tonificar, Flexibilidad

DATA_PATH = "data/rutinas.json"

class RutinaService:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(DATA_PATH):
            with open(DATA_PATH, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

        self._mapa = {
            "bajar_peso": BajarPeso(),
            "volumen": GanarVolumen(),
            "definicion": DefinicionMuscular(),
            "tonificar": Tonificar(),
            "flexibilidad": Flexibilidad()
        }

    def generar_rutina_con_dias(self, objetivo_nombre):
        dias = random.randint(2, 7)
        rutina = self.generar_rutina(objetivo_nombre, dias)
        return rutina, dias

    def generar_rutina(self, objetivo_nombre, dias):
        estrategia = self._mapa.get(objetivo_nombre)
        if not estrategia:
            estrategia = self._mapa["tonificar"]

        ejercicios_totales = estrategia.obtener_ejercicios().copy()
        if len(ejercicios_totales) < 3:
            ejercicios_totales = ejercicios_totales * 3

        random.shuffle(ejercicios_totales)

        rutina = {}
        ejercicios_usados = set()

        for dia in range(1, dias + 1):
            disponibles = [e for e in ejercicios_totales if e not in ejercicios_usados]


            if len(disponibles) < 3:
                ejercicios_usados.clear()
                disponibles = ejercicios_totales.copy()
                random.shuffle(disponibles)

            ejercicios_dia = random.sample(disponibles, 3)
            ejercicios_usados.update(ejercicios_dia)

            rutina[f"Día {dia}"] = ejercicios_dia

        return rutina

    def guardar_rutina(self, usuario_nombre, objetivo, rutina, dias):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            rutinas = json.load(f)
        rutinas.append({
            "usuario": usuario_nombre,
            "objetivo": objetivo,
            "dias": dias,
            "rutina": rutina
        })
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(rutinas, f, ensure_ascii=False, indent=4)

    def obtener_rutinas(self):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
