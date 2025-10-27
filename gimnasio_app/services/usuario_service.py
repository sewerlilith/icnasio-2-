import json
import os


class UsuarioService:
    def __init__(self, data_path: str = "data/usuarios.json"):
        self.data_path = data_path
        dirpath = os.path.dirname(self.data_path) or "data"
        os.makedirs(dirpath, exist_ok=True)
        if not os.path.exists(self.data_path):
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

    def guardar_usuario(self, usuario_dict):
        with open(self.data_path, "r", encoding="utf-8") as f:
            usuarios = json.load(f)
        usuarios.append(usuario_dict)
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, ensure_ascii=False, indent=4)

    def obtener_usuarios(self):
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)