import json, os, random
from models.objetivos import BajarPeso, GanarVolumen, DefinicionMuscular, Tonificar, Flexibilidad


class RutinaService:
    def __init__(self, data_path: str = "data/rutinas.json", mapa: dict = None):
        self.data_path = data_path
        dirpath = os.path.dirname(self.data_path) or "data"
        os.makedirs(dirpath, exist_ok=True)
        if not os.path.exists(self.data_path):
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

        if mapa is not None:
            self._mapa = mapa
        else:
            self._mapa = {
                "bajar_peso": BajarPeso(),
                "volumen": GanarVolumen(),
                "definicion": DefinicionMuscular(),
                "tonificar": Tonificar(),
                "flexibilidad": Flexibilidad()
            }

    def generar_rutina_con_dias(self, objetivo_nombre):
        dias = random.randint(2, 5)
        rutina = self.generar_rutina(objetivo_nombre, dias)
        return rutina, dias

    def generar_rutina(self, objetivo_nombre, dias):
        estrategia = self._mapa.get(objetivo_nombre)
        if not estrategia:
            estrategia = self._mapa["tonificar"]
        # ahora los ejercicios son diccionarios con 'name', 'zone' y 'image'
        ejercicios_totales = estrategia.obtener_ejercicios().copy()

        # construir mapeo zone -> lista de ejercicios
        zone_map = {}
        for e in ejercicios_totales:
            zone = e.get('zone', 'general')
            zone_map.setdefault(zone, []).append(e)

        # si no hay zonas (caso raro), usar todos como 'general'
        if not zone_map:
            zone_map = {'general': ejercicios_totales}

        # elegir una lista de zonas para los dias: rotar entre zonas disponibles
        zonas = list(zone_map.keys())
        rutina = {}

        # mantenemos historial de ejercicios usados por zona para evitar repeticiones
        usados_por_zona = {z: set() for z in zonas}

        for dia in range(1, dias + 1):
            # seleccionar zona para este día (rotación simple)
            zona = zonas[(dia - 1) % len(zonas)] if zonas else 'general'

            # Preferir ejercicios de la zona que no se hayan usado aún en esa zona
            pool_zone = [e for e in zone_map[zona] if e['name'] not in usados_por_zona[zona]]

            seleccion = []

            if len(pool_zone) >= 3:
                seleccion = random.sample(pool_zone, 3)
            else:
                # Construir fallback de ejercicios únicos de otras zonas que no estén marcados como usados
                fallback = []
                seen = set()
                # first add remaining zone items
                for e in pool_zone:
                    if e['name'] not in seen:
                        fallback.append(e)
                        seen.add(e['name'])

                # then add from other zones
                for oz in zonas:
                    if oz == zona:
                        continue
                    for e in zone_map[oz]:
                        # no agregar si el ejercicio ya fue usado en su zona (evitar reuse across days)
                        if e['name'] in usados_por_zona.get(oz, set()):
                            continue
                        if e['name'] in seen:
                            continue
                        fallback.append(e)
                        seen.add(e['name'])
                        if len(fallback) >= 3:
                            break
                    if len(fallback) >= 3:
                        break

                if len(fallback) >= 3:
                    seleccion = random.sample(fallback, 3)
                else:
                    # Como último recurso, permitir elegir de todo el pool (incluye ya usados globalmente)
                    all_unique = []
                    seen2 = set()
                    for e in ejercicios_totales:
                        if e['name'] not in seen2:
                            all_unique.append(e)
                            seen2.add(e['name'])

                    if len(all_unique) >= 3:
                        seleccion = random.sample(all_unique, 3)
                    else:
                        # si incluso así no hay suficientes únicos, elegir con posible duplicado pero intentar ser diverso
                        seleccion = []
                        while len(seleccion) < 3:
                            candidate = random.choice(ejercicios_totales)
                            if candidate['name'] not in [s['name'] for s in seleccion]:
                                seleccion.append(candidate)
                            else:
                                # si no hay alternativa, aceptar duplicado
                                seleccion.append(candidate)

            # Añadir series/reps a cada ejercicio según objetivo y zona
            ejercicios_dia = []
            for e in seleccion:
                item = e.copy()
                sr = self._assign_sets_reps(objetivo_nombre, item.get('zone', 'general'))
                item['series'] = sr['series']
                item['reps'] = sr['reps']
                item['reps_unit'] = sr.get('reps_unit', 'reps')
                ejercicios_dia.append(item)

            rutina[f"Día {dia}"] = ejercicios_dia
            usados_por_zona[zona].update(e['name'] for e in seleccion)

        return rutina

    def _assign_sets_reps(self, objetivo, zone):
        """Devuelve un dict con keys: series, reps, reps_unit según objetivo y zona."""
        # Defaults (determinísticos para series por objetivo)
        reps_unit = 'reps'

        if objetivo == 'volumen':
            series = 4
            reps = 8
        elif objetivo == 'definicion':
            series = 3
            reps = 15
        elif objetivo == 'bajar_peso':
            if zone in ('cardio', 'fullbody'):
                series = 1
                reps = 20
                reps_unit = 'min'
            else:
                series = 3
                reps = 12
        elif objetivo == 'tonificar':
            series = 3
            reps = 12
        elif objetivo == 'flexibilidad':
            series = 2
            reps = 30
            reps_unit = 'seg'
        else:
            series = 3
            reps = 10

        return {'series': series, 'reps': reps, 'reps_unit': reps_unit}

    def guardar_rutina(self, usuario_nombre, objetivo, rutina, dias):
        with open(self.data_path, "r", encoding="utf-8") as f:
            rutinas = json.load(f)
        rutinas.append({
            "usuario": usuario_nombre,
            "objetivo": objetivo,
            "dias": dias,
            "rutina": rutina
        })
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(rutinas, f, ensure_ascii=False, indent=4)

    def obtener_rutinas(self):
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)