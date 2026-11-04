import csv
import io
import time
from datetime import timedelta

from flask import Blueprint, Response, abort, flash, redirect, render_template, request, send_file, url_for
from openpyxl import load_workbook
from werkzeug.security import check_password_hash, generate_password_hash

from . import archivos
from . import basedatos as db
from .auth import verificar_sesion
from .utilidades import (
    DIAS, ENTREGAS, ESTADOS, MEDIOS_PAGO, MESES, TEMAS, TIPOS,
    fecha_valida, fila_planilla_a_libro, hora_valida, hoy_argentina, money,
)

bp = Blueprint("rutas", __name__)
bp.before_request(verificar_sesion)


def _entero(valor, por_defecto=None):
    try:
        return int(float(valor))
    except (TypeError, ValueError):
        return por_defecto


# ---------- PANEL ----------

@bp.route("/")
def panel():
    hoy = hoy_argentina()
    libros = db.listar_libros()
    disponibles = [b for b in libros if not b["vendido"]]
    turnos = db.listar_turnos()
    futuros = [t for t in turnos if t["fecha"] >= hoy.isoformat()]
    ventas_mes = db.listar_ventas_del_mes(hoy.year, hoy.month)

    ultimas_ventas = []
    for v in sorted(db.listar_ventas(), key=lambda v: v["fecha"], reverse=True)[:5]:
        libro = db.obtener_libro(v["libro_id"])
        ultimas_ventas.append((v, libro))

    proximos_turnos = sorted(futuros, key=lambda t: (t["fecha"], t["hora"]))[:4]

    alertas = []
    for libro in db.listar_instagram_pendiente():
        alertas.append({"tipo": "instagram", "libro": libro})
    for libro in disponibles:
        if not libro["precio"]:
            alertas.append({"tipo": "sin_precio", "libro": libro})
    for libro in disponibles:
        if libro["anio"] and libro["anio"] < 1950:
            alertas.append({"tipo": "antiguo", "libro": libro})
    alertas = alertas[:5]

    return render_template(
        "panel.html",
        vendido_mes=money(sum(v["precio"] for v in ventas_mes)),
        libros_mes=len(ventas_mes),
        disponibles=len(disponibles),
        valor_estante=money(sum(b["precio"] * b["ejemplares"] for b in disponibles)),
        turnos_futuros=len(futuros),
        ultimas_ventas=ultimas_ventas,
        proximos_turnos=proximos_turnos,
        alertas=alertas,
    )


@bp.route("/instagram/<libro_id>/confirmar", methods=["POST"])
def confirmar_instagram(libro_id):
    db.confirmar_post_instagram(libro_id)
    flash("Anotado.")
    return redirect(request.referrer or url_for("rutas.panel"))


# ---------- CATÁLOGO ----------

@bp.route("/catalogo")
def catalogo():
    q = request.args.get("q", "")
    tema = request.args.get("tema", "")
    tipo = request.args.get("tipo", "")
    disp = request.args.get("disp", "")
    libros = db.listar_libros(q, tema, tipo, disp)
    todos = db.listar_libros()
    return render_template(
        "catalogo.html",
        libros=libros,
        total=len(todos),
        con_ventas=db.listar_ids_libros_con_ventas(),
        q=q, tema=tema, tipo=tipo, disp=disp,
        TEMAS=TEMAS, TIPOS=TIPOS, ESTADOS=ESTADOS,
    )


def _datos_libro_de_formulario():
    return {
        "titulo": request.form.get("titulo", "").strip(),
        "autor": request.form.get("autor", "").strip(),
        "editorial": request.form.get("editorial", "").strip(),
        "anio": _entero(request.form.get("anio")),
        "pais": request.form.get("pais", "Argentina").strip(),
        "tapa": request.form.get("tapa", "Tapa blanda"),
        "paginas": _entero(request.form.get("paginas")),
        "tema": request.form.get("tema", TEMAS[0]),
        "tipo": request.form.get("tipo", TIPOS[0]),
        "estado": request.form.get("estado", ESTADOS[0]),
        "precio": max(0, _entero(request.form.get("precio"), 0)),
        "ilustrado": 1 if request.form.get("ilustrado") else 0,
        "nota": request.form.get("nota", "").strip(),
        "ejemplares": max(0, _entero(request.form.get("ejemplares"), 1)),
    }


def _validar_archivos_de_formulario():
    """Revisa la portada y el PDF que vinieron en el formulario, antes de
    tocar la base. Devuelve ({campo: (archivo, extension)}, error)."""
    nuevos = {}
    for campo, validar in (("portada", archivos.validar_portada), ("pdf", archivos.validar_pdf)):
        archivo = request.files.get(campo)
        if not archivos.hay_archivo(archivo):
            continue
        try:
            nuevos[campo] = (archivo, validar(archivo))
        except archivos.ArchivoInvalido as e:
            return {}, str(e)
    return nuevos, None


def _aplicar_archivos(libro_id, libro_anterior, nuevos, quitar=()):
    """Guarda los archivos nuevos, quita los marcados y borra del disco
    los que quedaron reemplazados."""
    for campo in ("portada", "pdf"):
        anterior = libro_anterior[campo] if libro_anterior else ""
        if campo in nuevos:
            archivo, extension = nuevos[campo]
            nombre = archivos.crear_archivo(libro_id, campo, extension, archivo)
        elif campo in quitar:
            nombre = ""
        else:
            continue
        db.actualizar_archivo_libro(libro_id, campo, nombre)
        if anterior and anterior != nombre:
            archivos.eliminar_archivo(anterior)


@bp.route("/catalogo/crear", methods=["POST"])
def crear_libro():
    datos = _datos_libro_de_formulario()
    if not datos["titulo"]:
        flash("Falta el título del libro.")
        return redirect(url_for("rutas.catalogo"))
    nuevos, error = _validar_archivos_de_formulario()
    if error:
        flash(f"{error} El libro no se cargó.")
        return redirect(url_for("rutas.catalogo"))
    datos["id"] = f"l{int(time.time() * 1000)}"
    db.crear_libro(datos)
    _aplicar_archivos(datos["id"], None, nuevos)
    flash("Libro cargado: ya aparece en la vitrina.")
    return redirect(url_for("rutas.catalogo"))


@bp.route("/catalogo/<libro_id>/actualizar", methods=["POST"])
def actualizar_libro(libro_id):
    if not db.existe_libro(libro_id):
        flash("Ese libro ya no existe.")
        return redirect(url_for("rutas.catalogo"))
    datos = _datos_libro_de_formulario()
    if not datos["titulo"]:
        flash("Falta el título del libro.")
        return redirect(url_for("rutas.catalogo"))
    nuevos, error = _validar_archivos_de_formulario()
    if error:
        flash(f"{error} No se guardaron los cambios.")
        return redirect(url_for("rutas.catalogo"))
    anterior = db.obtener_libro(libro_id)
    db.actualizar_libro(libro_id, datos)
    quitar = [c for c in ("portada", "pdf") if request.form.get(f"quitar_{c}")]
    _aplicar_archivos(libro_id, anterior, nuevos, quitar)
    flash("Libro actualizado.")
    return redirect(url_for("rutas.catalogo"))


@bp.route("/catalogo/<libro_id>/eliminar", methods=["POST"])
def eliminar_libro(libro_id):
    libro = db.obtener_libro(libro_id)
    if db.eliminar_libro(libro_id):
        if libro:
            archivos.eliminar_archivo(libro["portada"])
            archivos.eliminar_archivo(libro["pdf"])
        flash("Libro eliminado del catálogo.")
    else:
        flash("Ese libro tiene ventas registradas: no se puede borrar, "
              "queda en el catálogo como parte del historial.")
    return redirect(url_for("rutas.catalogo"))


@bp.route("/catalogo/<libro_id>/portada")
def portada_libro(libro_id):
    libro = db.obtener_libro(libro_id)
    ruta = archivos.obtener_ruta_archivo(libro["portada"]) if libro else None
    if ruta is None:
        abort(404)
    extension = ruta.suffix.lstrip(".")
    # La URL cambia con cada portada nueva (?v=nombre), así que se puede
    # cachear en el navegador sin miedo a mostrar una vieja.
    return send_file(ruta, mimetype=archivos.TIPOS_PORTADA.get(extension), max_age=31536000)


@bp.route("/catalogo/<libro_id>/pdf")
def pdf_libro(libro_id):
    libro = db.obtener_libro(libro_id)
    ruta = archivos.obtener_ruta_archivo(libro["pdf"]) if libro else None
    if ruta is None:
        abort(404)
    nombre = "".join(c for c in libro["titulo"] if c.isalnum() or c in " -_").strip() or "libro"
    return send_file(ruta, mimetype="application/pdf", download_name=f"{nombre}.pdf",
                     as_attachment=request.args.get("descargar") == "1")


@bp.route("/catalogo/planilla.csv")
def catalogo_csv():
    columnas = ["nro", "titulo", "autor", "editorial", "anio", "pais", "tapa",
                "paginas", "tema", "tipo", "estado", "precio", "ejemplares", "vendido"]
    buffer = io.StringIO()
    escritor = csv.writer(buffer, delimiter=";")
    escritor.writerow(columnas)
    for libro in db.listar_libros():
        fila = [libro[c] for c in columnas[:-1]]
        fila.append("sí" if libro["vendido"] else "no")
        escritor.writerow(fila)
    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=azoth-catalogo.csv"},
    )


@bp.route("/catalogo/importar", methods=["GET", "POST"])
def importar_catalogo():
    if request.method == "GET":
        return render_template("importar.html")

    archivo = request.files.get("archivo")
    if not archivo or not archivo.filename:
        flash("Elegí el archivo de la planilla.")
        return redirect(url_for("rutas.importar_catalogo"))
    if not archivo.filename.lower().endswith((".xlsx", ".xlsm")):
        flash("Tiene que ser un archivo .xlsx (la planilla de ejemplo ya viene en ese formato).")
        return redirect(url_for("rutas.importar_catalogo"))

    try:
        libro_excel = load_workbook(archivo, data_only=True, read_only=True)
    except Exception:
        flash("No se pudo abrir ese archivo. ¿Es un .xlsx válido?")
        return redirect(url_for("rutas.importar_catalogo"))

    hoja = libro_excel["Catálogo"] if "Catálogo" in libro_excel.sheetnames else libro_excel.worksheets[0]

    fila_encabezado = None
    for fila in hoja.iter_rows(min_row=1, max_row=10):
        if fila and str(fila[0].value or "").strip().lower() == "título":
            fila_encabezado = fila[0].row
            break
    if fila_encabezado is None:
        fila_encabezado = 1

    importados = 0
    for i, fila in enumerate(hoja.iter_rows(min_row=fila_encabezado + 1, values_only=True)):
        datos = fila_planilla_a_libro(fila)
        if datos is None:
            continue
        datos["id"] = f"l{int(time.time() * 1000)}{i}"
        db.crear_libro(datos)
        importados += 1

    if importados:
        flash(f"Se importaron {importados} libros al catálogo.")
    else:
        flash("No se encontró ningún libro con título en esa planilla.")
    return redirect(url_for("rutas.catalogo"))


# ---------- VITRINA ----------

@bp.route("/vitrina")
def vitrina():
    q = request.args.get("q", "")
    tema = request.args.get("tema", "")
    libros = db.listar_libros(q, tema, "", "1")
    return render_template("vitrina.html", libros=libros, q=q, tema=tema, TEMAS=TEMAS)


# ---------- VENTAS ----------

@bp.route("/ventas")
def ventas():
    hoy = hoy_argentina()
    ventas_mes = db.listar_ventas_del_mes(hoy.year, hoy.month)
    mes_pasado = hoy.replace(day=1) - timedelta(days=1)
    ventas_mes_pasado = db.listar_ventas_del_mes(mes_pasado.year, mes_pasado.month)

    todas = db.listar_ventas()
    filas = [(v, db.obtener_libro(v["libro_id"])) for v in todas]

    por_tema, por_medio = {}, {}
    for v, libro in filas:
        tema = libro["tema"] if libro else "Otros"
        por_tema[tema] = por_tema.get(tema, 0) + v["precio"]
        por_medio[v["medio"]] = por_medio.get(v["medio"], 0) + v["precio"]
    barras_tema = sorted(por_tema.items(), key=lambda kv: kv[1], reverse=True)
    barras_medio = sorted(por_medio.items(), key=lambda kv: kv[1], reverse=True)
    max_tema = barras_tema[0][1] if barras_tema else 1
    max_medio = barras_medio[0][1] if barras_medio else 1

    total_mes = sum(v["precio"] for v in ventas_mes)
    con_envio = sum(1 for v in ventas_mes if v["entrega"] == "Envío")

    disponibles = [b for b in db.listar_libros() if not b["vendido"]]

    return render_template(
        "ventas.html",
        filas=filas,
        total_mes=money(total_mes),
        cantidad_mes=len(ventas_mes),
        ticket_promedio=money(total_mes / len(ventas_mes)) if ventas_mes else money(0),
        con_envio=con_envio,
        total_mes_pasado=money(sum(v["precio"] for v in ventas_mes_pasado)),
        barras_tema=barras_tema, barras_medio=barras_medio,
        max_tema=max_tema, max_medio=max_medio,
        disponibles=disponibles,
        MEDIOS_PAGO=MEDIOS_PAGO, ENTREGAS=ENTREGAS,
    )


@bp.route("/ventas/crear", methods=["POST"])
def crear_venta():
    libro_id = request.form.get("libro_id", "")
    if not db.existe_libro(libro_id):
        flash("Elegí un libro del listado.")
        return redirect(url_for("rutas.ventas"))
    precio = max(0, _entero(request.form.get("precio"), 0))
    venta_id = db.crear_venta(
        hoy_argentina().isoformat(),
        libro_id,
        request.form.get("medio", MEDIOS_PAGO[0]),
        request.form.get("entrega", ENTREGAS[0]),
        precio,
    )
    if venta_id is None:
        flash("No quedan ejemplares de ese libro: la venta no se registró.")
        return redirect(url_for("rutas.ventas"))
    libro = db.obtener_libro(libro_id)
    if libro["ejemplares"] == 0:
        flash("Venta registrada · era el último ejemplar: falta marcar VENDIDO en el post.")
    else:
        flash(f"Venta registrada · quedan {libro['ejemplares']} ejemplares.")
    return redirect(url_for("rutas.ventas"))


@bp.route("/ventas/<int:venta_id>/eliminar", methods=["POST"])
def eliminar_venta(venta_id):
    db.eliminar_venta(venta_id)
    flash("Venta anulada: el ejemplar volvió al estante.")
    return redirect(url_for("rutas.ventas"))


# ---------- TURNOS DE TATUAJE ----------

@bp.route("/turnos")
def turnos():
    hoy = hoy_argentina()
    todos = db.listar_turnos()
    futuros = [t for t in todos if t["fecha"] >= hoy.isoformat()]

    inicio_semana = hoy - timedelta(days=hoy.weekday())
    semana = []
    for i in range(7):
        x = inicio_semana + timedelta(days=i)
        iso = x.isoformat()
        dw = (x.weekday() + 1) % 7
        turnos_dia = sorted(
            (t for t in todos if t["fecha"] == iso), key=lambda t: t["hora"]
        )
        semana.append({
            "fecha": iso,
            "dia": DIAS[dw],
            "dia_num": x.day,
            "mes": MESES[x.month - 1],
            "cerrado": dw in (0, 2),
            "es_hoy": iso == hoy.isoformat(),
            "manana": [t for t in turnos_dia if t["hora"] < "14:00"],
            "tarde": [t for t in turnos_dia if t["hora"] >= "14:00"],
        })

    return render_template(
        "turnos.html",
        turnos=todos,
        hoy=hoy,
        semana=semana,
        futuros=len(futuros),
        senas_cobradas=money(sum(t["sena"] for t in futuros)),
        saldo_a_cobrar=money(sum(t["total"] - t["sena"] for t in futuros)),
        sin_sena=sum(1 for t in futuros if t["estado"] == "Falta seña"),
        manana=(hoy + timedelta(days=1)).isoformat(),
    )


def _datos_turno_de_formulario():
    sena = max(0, _entero(request.form.get("sena"), 0))
    return {
        "fecha": request.form.get("fecha", ""),
        "hora": request.form.get("hora", "11:00"),
        "cliente": request.form.get("cliente", "").strip(),
        "diseno": request.form.get("diseno", "").strip(),
        "sesion": request.form.get("sesion", "1 de 1").strip() or "1 de 1",
        "total": max(0, _entero(request.form.get("total"), 0)),
        "sena": sena,
        "estado": request.form.get("estado") or ("Falta seña" if sena == 0 else "Confirmado"),
    }


def _error_turno(datos):
    if not (datos["fecha"] and datos["cliente"] and datos["diseno"]):
        return "Faltan datos del turno."
    if not fecha_valida(datos["fecha"]):
        return "La fecha del turno no es válida."
    if not hora_valida(datos["hora"]):
        return "La hora del turno no es válida (tiene que ser HH:MM)."
    return None


@bp.route("/turnos/crear", methods=["POST"])
def crear_turno():
    datos = _datos_turno_de_formulario()
    error = _error_turno(datos)
    if error:
        flash(error)
        return redirect(url_for("rutas.turnos"))
    db.crear_turno(datos)
    flash("Turno agendado.")
    return redirect(url_for("rutas.turnos"))


@bp.route("/turnos/<int:turno_id>/actualizar", methods=["POST"])
def actualizar_turno(turno_id):
    if not db.existe_turno(turno_id):
        flash("Ese turno ya no existe.")
        return redirect(url_for("rutas.turnos"))
    datos = _datos_turno_de_formulario()
    error = _error_turno(datos)
    if error:
        flash(error)
        return redirect(url_for("rutas.turnos"))
    db.actualizar_turno(turno_id, datos)
    flash("Turno actualizado.")
    return redirect(url_for("rutas.turnos"))


@bp.route("/turnos/<int:turno_id>/eliminar", methods=["POST"])
def eliminar_turno(turno_id):
    db.eliminar_turno(turno_id)
    flash("Turno eliminado.")
    return redirect(url_for("rutas.turnos"))


# ---------- CALCULADORA DE COSTOS ----------

@bp.route("/calculadora")
def calculadora():
    costo = request.args.get("costo", "")
    margen = request.args.get("margen", "30")
    resultado = None
    costo_n = _entero(costo)
    margen_n = _entero(margen)
    if costo_n is not None and costo_n >= 0 and margen_n is not None:
        precio_markup = costo_n * (1 + margen_n / 100)
        precio_margen = costo_n / (1 - margen_n / 100) if margen_n < 100 else None
        resultado = {
            "costo": costo_n,
            "margen": margen_n,
            "precio_markup": money(precio_markup),
            "ganancia_markup": money(precio_markup - costo_n),
            "precio_margen": money(precio_margen) if precio_margen is not None else None,
            "ganancia_margen": money(precio_margen - costo_n) if precio_margen is not None else None,
        }
    return render_template("calculadora.html", costo=costo, margen=margen, resultado=resultado)


# ---------- CONFIGURACIÓN ----------

@bp.route("/configuracion", methods=["GET"])
def configuracion():
    return render_template("configuracion.html", config=db.obtener_config_sitio())


@bp.route("/configuracion/clave", methods=["POST"])
def actualizar_clave():
    usuario = db.obtener_usuario()
    actual = request.form.get("clave_actual", "")
    nueva = request.form.get("clave_nueva", "")
    repetida = request.form.get("clave_nueva_repetida", "")
    if not check_password_hash(usuario["clave_hash"], actual):
        flash("La contraseña actual no es correcta.")
    elif len(nueva) < 4:
        flash("La contraseña nueva tiene que tener al menos 4 caracteres.")
    elif nueva != repetida:
        flash("Las dos contraseñas nuevas no coinciden.")
    else:
        db.actualizar_clave_usuario(generate_password_hash(nueva))
        flash("Contraseña actualizada.")
    return redirect(url_for("rutas.configuracion"))


@bp.route("/configuracion/sitio", methods=["POST"])
def actualizar_sitio():
    for clave in ("whatsapp_numero", "direccion", "horario_texto"):
        db.actualizar_configuracion(clave, request.form.get(clave, "").strip())
    flash("Datos del local actualizados.")
    return redirect(url_for("rutas.configuracion"))


@bp.route("/configuracion/instagram/agregar", methods=["POST"])
def agregar_instagram():
    etiqueta = request.form.get("etiqueta", "").strip()
    usuario = request.form.get("usuario", "").strip().lstrip("@")
    if not (etiqueta and usuario):
        flash("Faltan datos de la cuenta de Instagram.")
    else:
        db.agregar_instagram_cuenta(etiqueta, usuario)
        flash("Cuenta de Instagram agregada.")
    return redirect(url_for("rutas.configuracion"))


@bp.route("/configuracion/instagram/<int:cuenta_id>/eliminar", methods=["POST"])
def eliminar_instagram(cuenta_id):
    db.eliminar_instagram_cuenta(cuenta_id)
    flash("Cuenta de Instagram eliminada.")
    return redirect(url_for("rutas.configuracion"))
