import json
import sqlite3
from pathlib import Path

import click
from flask import current_app, g


def obtener_conexion():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def cerrar_conexion(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def inicializar_esquema():
    db = obtener_conexion()
    esquema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    db.executescript(esquema)
    _migrar(db)
    db.commit()


def _migrar(db):
    """Cambios de esquema sobre bases ya creadas (CREATE TABLE IF NOT EXISTS
    no agrega columnas nuevas a una tabla que ya existe)."""
    columnas = {f["name"] for f in db.execute("PRAGMA table_info(libros)")}
    if "ejemplares" not in columnas:
        db.execute("ALTER TABLE libros ADD COLUMN ejemplares INTEGER NOT NULL DEFAULT 1")
        db.execute("UPDATE libros SET ejemplares = 0 WHERE vendido = 1")
    for columna in ("portada", "pdf"):
        if columna not in columnas:
            db.execute(f"ALTER TABLE libros ADD COLUMN {columna} TEXT NOT NULL DEFAULT ''")


def registrar_comandos(app):
    app.teardown_appcontext(cerrar_conexion)
    app.cli.add_command(_comando_inicializar_db)


@click.command("init-db")
def _comando_inicializar_db():
    """Crea las tablas si no existen (no borra datos)."""
    inicializar_esquema()
    click.echo("Base de datos lista.")


def _fila_a_dict(fila):
    return dict(fila) if fila is not None else None


# ---------- usuario ----------

def existe_usuario():
    db = obtener_conexion()
    return db.execute("SELECT 1 FROM usuario WHERE id = 1").fetchone() is not None


def obtener_usuario():
    db = obtener_conexion()
    return _fila_a_dict(db.execute("SELECT * FROM usuario WHERE id = 1").fetchone())


def crear_usuario(nombre, clave_hash):
    db = obtener_conexion()
    db.execute(
        "INSERT INTO usuario (id, nombre, clave_hash) VALUES (1, ?, ?)",
        (nombre, clave_hash),
    )
    db.commit()


def actualizar_clave_usuario(clave_hash):
    db = obtener_conexion()
    db.execute("UPDATE usuario SET clave_hash = ? WHERE id = 1", (clave_hash,))
    db.commit()


# ---------- configuración (clave/valor) ----------

def listar_configuracion():
    db = obtener_conexion()
    filas = db.execute("SELECT clave, valor FROM configuracion").fetchall()
    return {f["clave"]: f["valor"] for f in filas}


def obtener_configuracion(clave, por_defecto=""):
    db = obtener_conexion()
    fila = db.execute(
        "SELECT valor FROM configuracion WHERE clave = ?", (clave,)
    ).fetchone()
    return fila["valor"] if fila else por_defecto


def actualizar_configuracion(clave, valor):
    db = obtener_conexion()
    db.execute(
        "INSERT INTO configuracion (clave, valor) VALUES (?, ?) "
        "ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor",
        (clave, valor),
    )
    db.commit()


_CONFIG_SITIO_DEFAULTS = {
    "whatsapp_numero": "5491137869154",
    "direccion": "Bolívar 1447, San Telmo",
    "horario_texto": "14 a 19 h · martes y domingo cerrado",
}


def obtener_config_sitio():
    guardado = listar_configuracion()
    config = {clave: guardado.get(clave, valor) or valor for clave, valor in _CONFIG_SITIO_DEFAULTS.items()}
    config["instagram_cuentas"] = listar_instagram_cuentas()
    return config


# ---------- cuentas de Instagram (pueden ser varias: librería, tatuajes, etc.) ----------

# Cuentas reales de Azoth. Se usan mientras no se haya guardado ninguna lista
# desde Configuración; la primera es la que usa la Vitrina.
_INSTAGRAM_DEFAULTS = [
    {"id": 1, "etiqueta": "Librería", "usuario": "azothlibreria"},
    {"id": 2, "etiqueta": "Tatuajes · Solar Estudio", "usuario": "solarestudioba"},
    {"id": 3, "etiqueta": "Silvio", "usuario": "silviocaveira"},
]


def listar_instagram_cuentas():
    crudo = obtener_configuracion("instagram_cuentas", None)
    if crudo is None:
        return [dict(c) for c in _INSTAGRAM_DEFAULTS]
    if not crudo:
        return []
    try:
        return json.loads(crudo)
    except (json.JSONDecodeError, TypeError):
        return []


def _guardar_instagram_cuentas(cuentas):
    actualizar_configuracion("instagram_cuentas", json.dumps(cuentas, ensure_ascii=False))


def agregar_instagram_cuenta(etiqueta, usuario):
    cuentas = listar_instagram_cuentas()
    siguiente_id = max((c["id"] for c in cuentas), default=0) + 1
    cuentas.append({"id": siguiente_id, "etiqueta": etiqueta, "usuario": usuario})
    _guardar_instagram_cuentas(cuentas)


def eliminar_instagram_cuenta(cuenta_id):
    cuentas = [c for c in listar_instagram_cuentas() if c["id"] != cuenta_id]
    _guardar_instagram_cuentas(cuentas)


# ---------- libros ----------

def existe_libro(libro_id):
    db = obtener_conexion()
    return db.execute(
        "SELECT 1 FROM libros WHERE id = ?", (libro_id,)
    ).fetchone() is not None


def obtener_libro(libro_id):
    db = obtener_conexion()
    return _fila_a_dict(
        db.execute("SELECT * FROM libros WHERE id = ?", (libro_id,)).fetchone()
    )


def listar_libros(buscar="", tema="", tipo="", disponibilidad=""):
    db = obtener_conexion()
    condiciones, parametros = [], []
    if buscar:
        condiciones.append("(titulo LIKE ? OR autor LIKE ? OR editorial LIKE ?)")
        comodin = f"%{buscar}%"
        parametros += [comodin, comodin, comodin]
    if tema:
        condiciones.append("tema = ?")
        parametros.append(tema)
    if tipo:
        condiciones.append("tipo = ?")
        parametros.append(tipo)
    if disponibilidad == "1":
        condiciones.append("vendido = 0")
    elif disponibilidad == "0":
        condiciones.append("vendido = 1")
    sql = "SELECT * FROM libros"
    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)
    sql += " ORDER BY nro DESC"
    return [dict(f) for f in db.execute(sql, parametros).fetchall()]


def obtener_libro_igual(titulo, autor="", editorial=""):
    """Un libro ya cargado con el mismo título, autor y editorial (sin
    importar mayúsculas ni tildes), o None."""
    from .utilidades import clave_libro

    buscada = clave_libro(titulo, autor, editorial)
    for libro in listar_libros():
        if clave_libro(libro["titulo"], libro["autor"], libro["editorial"]) == buscada:
            return libro
    return None


def siguiente_nro_libro():
    db = obtener_conexion()
    fila = db.execute("SELECT MAX(nro) AS m FROM libros").fetchone()
    return (fila["m"] or 0) + 1


def crear_libro(datos):
    db = obtener_conexion()
    datos = dict(datos)
    datos["nro"] = siguiente_nro_libro()
    datos["ejemplares"] = max(0, datos.get("ejemplares", 1) or 0)
    db.execute(
        """INSERT INTO libros
           (id, nro, titulo, autor, editorial, anio, pais, tapa, paginas,
            tema, tipo, estado, precio, ilustrado, nota, ejemplares, vendido)
           VALUES (:id, :nro, :titulo, :autor, :editorial, :anio, :pais, :tapa,
                   :paginas, :tema, :tipo, :estado, :precio, :ilustrado, :nota,
                   :ejemplares, :ejemplares = 0)""",
        datos,
    )
    db.commit()
    return datos["id"]


def actualizar_libro(libro_id, datos):
    """Actualiza los datos del libro, incluido el stock: si se repone
    (ejemplares > 0) el libro vuelve a estar disponible en la vitrina."""
    db = obtener_conexion()
    datos = dict(datos, id=libro_id)
    datos["ejemplares"] = max(0, datos.get("ejemplares", 1) or 0)
    db.execute(
        """UPDATE libros SET titulo=:titulo, autor=:autor, editorial=:editorial,
           anio=:anio, pais=:pais, tapa=:tapa, paginas=:paginas, tema=:tema,
           tipo=:tipo, estado=:estado, precio=:precio, ilustrado=:ilustrado,
           nota=:nota, ejemplares=:ejemplares, vendido=(:ejemplares = 0)
           WHERE id=:id""",
        datos,
    )
    if datos["ejemplares"] > 0:
        db.execute("DELETE FROM instagram_pendiente WHERE libro_id = ?", (libro_id,))
    db.commit()


def actualizar_archivo_libro(libro_id, campo, nombre):
    """Anota el archivo de portada o PDF del libro ('' = quitarlo)."""
    if campo not in ("portada", "pdf"):
        raise ValueError(f"campo de archivo desconocido: {campo}")
    db = obtener_conexion()
    db.execute(f"UPDATE libros SET {campo} = ? WHERE id = ?", (nombre, libro_id))
    db.commit()


def tiene_ventas(libro_id):
    db = obtener_conexion()
    return db.execute(
        "SELECT 1 FROM ventas WHERE libro_id = ? LIMIT 1", (libro_id,)
    ).fetchone() is not None


def listar_ids_libros_con_ventas():
    db = obtener_conexion()
    return {f["libro_id"] for f in db.execute("SELECT DISTINCT libro_id FROM ventas")}


def eliminar_libro(libro_id):
    """Borra un libro que nunca se vendió. Un libro con ventas no se borra:
    las ventas son el registro histórico. Devuelve False si no se borró."""
    if tiene_ventas(libro_id):
        return False
    db = obtener_conexion()
    db.execute("DELETE FROM instagram_pendiente WHERE libro_id = ?", (libro_id,))
    db.execute("DELETE FROM libros WHERE id = ?", (libro_id,))
    db.commit()
    return True


# ---------- avisos pendientes de Instagram ----------

def listar_instagram_pendiente():
    db = obtener_conexion()
    filas = db.execute(
        """SELECT l.* FROM instagram_pendiente p
           JOIN libros l ON l.id = p.libro_id
           ORDER BY l.nro DESC"""
    ).fetchall()
    return [dict(f) for f in filas]


def confirmar_post_instagram(libro_id):
    db = obtener_conexion()
    db.execute("DELETE FROM instagram_pendiente WHERE libro_id = ?", (libro_id,))
    db.commit()


# ---------- ventas ----------

def existe_venta(venta_id):
    db = obtener_conexion()
    return db.execute(
        "SELECT 1 FROM ventas WHERE id = ?", (venta_id,)
    ).fetchone() is not None


def obtener_venta(venta_id):
    db = obtener_conexion()
    return _fila_a_dict(
        db.execute("SELECT * FROM ventas WHERE id = ?", (venta_id,)).fetchone()
    )


def listar_ventas():
    db = obtener_conexion()
    filas = db.execute("SELECT * FROM ventas ORDER BY fecha DESC, id DESC").fetchall()
    return [dict(f) for f in filas]


def listar_ventas_del_mes(anio, mes):
    db = obtener_conexion()
    patron = f"{anio:04d}-{mes:02d}-%"
    filas = db.execute(
        "SELECT * FROM ventas WHERE fecha LIKE ? ORDER BY fecha DESC", (patron,)
    ).fetchall()
    return [dict(f) for f in filas]


def crear_venta(fecha, libro_id, medio, entrega, precio):
    """Registra la venta de un ejemplar y descuenta el stock, todo en una
    sola transacción. Devuelve el id de la venta, o None si no quedaban
    ejemplares (no se registra nada). Al vender el último ejemplar el libro
    queda VENDIDO y pendiente de marcar en el post de Instagram."""
    db = obtener_conexion()
    with db:
        cursor = db.execute(
            "UPDATE libros SET ejemplares = ejemplares - 1, vendido = (ejemplares - 1 = 0) "
            "WHERE id = ? AND ejemplares > 0",
            (libro_id,),
        )
        if cursor.rowcount == 0:
            return None
        cursor = db.execute(
            "INSERT INTO ventas (fecha, libro_id, medio, entrega, precio) "
            "VALUES (?, ?, ?, ?, ?)",
            (fecha, libro_id, medio, entrega, precio),
        )
        venta_id = cursor.lastrowid
        db.execute(
            "INSERT OR IGNORE INTO instagram_pendiente (libro_id) "
            "SELECT id FROM libros WHERE id = ? AND ejemplares = 0",
            (libro_id,),
        )
    return venta_id


def eliminar_venta(venta_id):
    """Anula una venta cargada por error: el ejemplar vuelve al estante."""
    db = obtener_conexion()
    venta = obtener_venta(venta_id)
    if venta is None:
        return False
    with db:
        db.execute("DELETE FROM ventas WHERE id = ?", (venta_id,))
        db.execute(
            "UPDATE libros SET ejemplares = ejemplares + 1, vendido = 0 WHERE id = ?",
            (venta["libro_id"],),
        )
        db.execute("DELETE FROM instagram_pendiente WHERE libro_id = ?", (venta["libro_id"],))
    return True


# ---------- turnos ----------

def existe_turno(turno_id):
    db = obtener_conexion()
    return db.execute(
        "SELECT 1 FROM turnos WHERE id = ?", (turno_id,)
    ).fetchone() is not None


def obtener_turno(turno_id):
    db = obtener_conexion()
    return _fila_a_dict(
        db.execute("SELECT * FROM turnos WHERE id = ?", (turno_id,)).fetchone()
    )


def listar_turnos():
    db = obtener_conexion()
    filas = db.execute(
        "SELECT * FROM turnos ORDER BY fecha ASC, hora ASC"
    ).fetchall()
    return [dict(f) for f in filas]


def siguiente_nro_turno():
    db = obtener_conexion()
    fila = db.execute("SELECT MAX(nro) AS m FROM turnos").fetchone()
    return (fila["m"] or 0) + 1


def crear_turno(datos):
    db = obtener_conexion()
    datos = dict(datos)
    datos["nro"] = siguiente_nro_turno()
    db.execute(
        """INSERT INTO turnos (nro, fecha, hora, cliente, diseno, sesion, total, sena, estado)
           VALUES (:nro, :fecha, :hora, :cliente, :diseno, :sesion, :total, :sena, :estado)""",
        datos,
    )
    db.commit()


def actualizar_turno(turno_id, datos):
    db = obtener_conexion()
    datos = dict(datos, id=turno_id)
    db.execute(
        """UPDATE turnos SET fecha=:fecha, hora=:hora, cliente=:cliente,
           diseno=:diseno, sesion=:sesion, total=:total, sena=:sena, estado=:estado
           WHERE id=:id""",
        datos,
    )
    db.commit()


def eliminar_turno(turno_id):
    db = obtener_conexion()
    db.execute("DELETE FROM turnos WHERE id = ?", (turno_id,))
    db.commit()
