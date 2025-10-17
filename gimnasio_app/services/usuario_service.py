import json
import os

DATA_PATH = "data/usuarios.json"

class UsuarioService:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(DATA_PATH):
            with open(DATA_PATH, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

    def guardar_usuario(self, usuario_dict):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            usuarios = json.load(f)
        usuarios.append(usuario_dict)
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, ensure_ascii=False, indent=4)

    def obtener_usuarios(self):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
