import threading
import time
from functools import wraps
from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from . import basedatos as db

bp = Blueprint("auth", __name__)

# Contraseñas nuevas: mínimo 8 caracteres (el sistema puede quedar accesible
# desde internet con Cloudflare Tunnel). Las de 4 que ya existan siguen
# sirviendo para entrar.
CLAVE_MINIMA = 8

# Límite de intentos: después de INTENTOS_MAXIMOS contraseñas incorrectas
# desde la misma dirección, el login queda bloqueado BLOQUEO_SEGUNDOS.
INTENTOS_MAXIMOS = 5
BLOQUEO_SEGUNDOS = 5 * 60
_intentos = {}          # ip -> (fallos, hora del primer fallo)
_candado = threading.Lock()


def _ip_cliente():
    """IP de quien intenta entrar. Detrás de Cloudflare Tunnel todas las
    requests llegan desde 127.0.0.1 (cloudflared corre en la misma PC), y la
    IP real viene en CF-Connecting-IP. Ese encabezado solo se cree si la
    request viene de la propia PC: desde el WiFi cualquiera podría inventarlo."""
    ip = request.remote_addr or "?"
    if ip in ("127.0.0.1", "::1"):
        return request.headers.get("CF-Connecting-IP", ip)
    return ip


def _segundos_bloqueado(ip):
    with _candado:
        fallos, desde = _intentos.get(ip, (0, 0))
        if fallos < INTENTOS_MAXIMOS:
            return 0
        restante = BLOQUEO_SEGUNDOS - (time.monotonic() - desde)
        if restante <= 0:
            _intentos.pop(ip, None)
            return 0
        return int(restante) + 1


def _anotar_fallo(ip):
    with _candado:
        fallos, desde = _intentos.get(ip, (0, time.monotonic()))
        if time.monotonic() - desde > BLOQUEO_SEGUNDOS:
            fallos, desde = 0, time.monotonic()
        _intentos[ip] = (fallos + 1, desde)


def _olvidar_fallos(ip):
    with _candado:
        _intentos.pop(ip, None)


def destino_seguro(siguiente):
    """Solo se vuelve a una página de este mismo sistema: '/ventas' sí,
    '//otro-sitio.com' o 'https://otro-sitio.com' no (redirección abierta)."""
    if not siguiente or not siguiente.startswith("/") or siguiente.startswith(("//", "/\\")):
        return None
    partes = urlsplit(siguiente.replace("\\", "/"))
    if partes.scheme or partes.netloc:
        return None
    return siguiente


def error_clave_nueva(clave, repetida):
    if len(clave) < CLAVE_MINIMA:
        return f"La contraseña tiene que tener al menos {CLAVE_MINIMA} caracteres."
    if clave != repetida:
        return "Las dos contraseñas no coinciden."
    return None


def verificar_sesion():
    """Para usar con Blueprint.before_request: corta la request con un
    redirect si hace falta loguearse; si no, deja pasar (devuelve None)."""
    if not db.existe_usuario():
        return redirect(url_for("auth.primer_ingreso"))
    if not session.get("autenticado"):
        return redirect(url_for("auth.login", siguiente=request.path))
    return None


def login_requerido(vista):
    """Decorador para proteger una vista suelta fuera de un blueprint."""

    @wraps(vista)
    def envoltorio(*args, **kwargs):
        respuesta = verificar_sesion()
        if respuesta is not None:
            return respuesta
        return vista(*args, **kwargs)

    return envoltorio


@bp.route("/primer-ingreso", methods=["GET", "POST"])
def primer_ingreso():
    if db.existe_usuario():
        return redirect(url_for("auth.login"))

    error = None
    if request.method == "POST":
        nombre = request.form.get("nombre", "Silvio").strip() or "Silvio"
        clave = request.form.get("clave", "")
        clave_repetida = request.form.get("clave_repetida", "")
        error = error_clave_nueva(clave, clave_repetida)
        if error is None:
            db.crear_usuario(nombre, generate_password_hash(clave))
            session.clear()
            # Sesión permanente (31 días): en el celular no hay que volver a
            # escribir la contraseña cada vez que se cierra el navegador.
            session.permanent = True
            session["autenticado"] = True
            session["nombre"] = nombre
            flash("Contraseña creada. Este sistema ya es solo tuyo.")
            return redirect(url_for("rutas.panel"))

    return render_template("primer_ingreso.html", error=error)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if not db.existe_usuario():
        return redirect(url_for("auth.primer_ingreso"))

    error = None
    siguiente = request.args.get("siguiente") or request.form.get("siguiente") or ""
    if request.method == "POST":
        ip = _ip_cliente()
        bloqueo = _segundos_bloqueado(ip)
        if bloqueo:
            minutos = (bloqueo + 59) // 60
            error = (f"Demasiados intentos fallidos. Esperá {minutos} "
                     f"minuto{'s' if minutos != 1 else ''} y probá de nuevo.")
            return render_template("login.html", error=error, siguiente=siguiente), 429
        clave = request.form.get("clave", "")
        usuario = db.obtener_usuario()
        if usuario and check_password_hash(usuario["clave_hash"], clave):
            _olvidar_fallos(ip)
            session.clear()
            # Sesión permanente (31 días): en el celular no hay que volver a
            # escribir la contraseña cada vez que se cierra el navegador.
            session.permanent = True
            session["autenticado"] = True
            session["nombre"] = usuario["nombre"]
            return redirect(destino_seguro(siguiente) or url_for("rutas.panel"))
        _anotar_fallo(ip)
        error = "Contraseña incorrecta."

    return render_template("login.html", error=error, siguiente=siguiente)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
