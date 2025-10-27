from services.usuario_service import UsuarioService
from services.rutina_service import RutinaService


class Container:
    def __init__(self, config: dict = None):
        self._config = config or {}
        self._singletons = {}
        self._overrides = {}

    def override(self, name: str, instance):
        self._overrides[name] = instance
        if name in self._singletons:
            del self._singletons[name]

    def usuario_service(self):
        if 'usuario_service' in self._overrides:
            return self._overrides['usuario_service']
        if 'usuario_service' not in self._singletons:
            data_path = self._config.get('usuarios_path', 'data/usuarios.json')
            self._singletons['usuario_service'] = UsuarioService(data_path)
        return self._singletons['usuario_service']

    def rutina_service(self):
        if 'rutina_service' in self._overrides:
            return self._overrides['rutina_service']
        if 'rutina_service' not in self._singletons:
            data_path = self._config.get('rutinas_path', 'data/rutinas.json')
            self._singletons['rutina_service'] = RutinaService(data_path)
        return self._singletons['rutina_service']


def create_container(config: dict = None):
    return Container(config)
