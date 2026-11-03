import secrets
from pathlib import Path

from flask import Flask

from . import basedatos as db
from . import rutas, auth
from .utilidades import (
    TAPAS, ficha, ficha_turno, fecha_corta, glifo, tono, estado_local,
    texto_post_instagram, mensaje_consulta_instagram, money, precio_o_consultar,
)


def _clave_secreta(carpeta_instance):
    archivo = Path(carpeta_instance) / "clave_secreta.txt"
    if archivo.exists():
        return archivo.read_text(encoding="utf-8").strip()
    archivo.parent.mkdir(parents=True, exist_ok=True)
    clave = secrets.token_hex(32)
    archivo.write_text(clave, encoding="utf-8")
    return clave


def create_app(config_extra=None):
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    app.config.from_mapping(
        SECRET_KEY=_clave_secreta(app.instance_path),
        DATABASE=str(Path(app.instance_path) / "azoth.db"),
    )
    if config_extra:
        app.config.from_mapping(config_extra)

    db.registrar_comandos(app)
    with app.app_context():
        db.inicializar_esquema()

    app.register_blueprint(auth.bp)
    app.register_blueprint(rutas.bp)

    app.jinja_env.filters["money"] = money
    app.jinja_env.filters["fecha_corta"] = fecha_corta
    app.jinja_env.globals.update(
        TAPAS=TAPAS,
        ficha=ficha,
        ficha_turno=ficha_turno,
        glifo=glifo,
        tono=tono,
        precio_o_consultar=precio_o_consultar,
        texto_post_instagram=texto_post_instagram,
        mensaje_consulta_instagram=mensaje_consulta_instagram,
    )

    @app.context_processor
    def inyectar_contexto_global():
        return {"estado_local": estado_local(), "sitio": db.obtener_config_sitio()}

    return app
