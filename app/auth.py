from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from . import basedatos as db

bp = Blueprint("auth", __name__)


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
        if len(clave) < 4:
            error = "La contraseña tiene que tener al menos 4 caracteres."
        elif clave != clave_repetida:
            error = "Las dos contraseñas no coinciden."
        else:
            db.crear_usuario(nombre, generate_password_hash(clave))
            session.clear()
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
        clave = request.form.get("clave", "")
        usuario = db.obtener_usuario()
        if usuario and check_password_hash(usuario["clave_hash"], clave):
            session.clear()
            session["autenticado"] = True
            session["nombre"] = usuario["nombre"]
            destino = siguiente if siguiente.startswith("/") else url_for("rutas.panel")
            return redirect(destino)
        error = "Contraseña incorrecta."

    return render_template("login.html", error=error, siguiente=siguiente)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
