import re
from datetime import date, datetime
from zoneinfo import ZoneInfo

TEMAS = [
    "Alquimia", "Hermetismo", "Cábala", "Magia", "Grimorios", "Thelema",
    "Tarot", "Astrología", "Teosofía", "Masonería", "Antroposofía",
    "Espiritismo", "Demonología", "Mitología", "Obra original",
]
TIPOS = ["Nuevo", "Nuevo de depósito", "Usado", "Descatalogado", "Antigüedad", "Obra original"]
ESTADOS = [
    "Excelente estado, sin roturas, ni escritos",
    "Sin roturas, ni escritos",
    "Con subrayados en lápiz suave",
    "Con algunos detalles (ver nota)",
    "Original firmado",
]
TAPAS = ["Tapa blanda", "Tapa dura", "Tapa dura entelada", "Tapa blanda con solapas"]
MEDIOS_PAGO = ["Transferencia", "Efectivo", "Mercado Pago"]
ENTREGAS = ["En el local", "Envío"]

_SEF = [(12, 2.5), (17, 6), (7, 6), (17, 10.5), (7, 10.5), (12, 12),
        (17, 15.5), (7, 15.5), (12, 18), (12, 21.5)]
_SEFIROT = "".join(
    f'<circle cx="{x}" cy="{y}" r="1.25" fill="#101114"/>' for x, y in _SEF
)

GLIFO = {
    "Alquimia": '<path d="M12 3 19 14H5Z"/><path d="M12 14v8M8.5 17.5h7M9.5 20.2h5"/>',
    "Hermetismo": '<circle cx="12" cy="13" r="4"/><path d="M8 5a4 4 0 0 0 8 0M12 17v5M9.5 19.5h5"/>',
    "Cábala": '<path d="M12 2.5 17 6M12 2.5 7 6M7 6h10M17 6v4.5M7 6v4.5M17 10.5 12 12 7 10.5M12 12l5 3.5M12 12l-5 3.5M17 15.5 12 18 7 15.5M12 18v3.5"/>' + _SEFIROT,
    "Magia": '<circle cx="12" cy="12" r="9.8"/><path d="M12 3 17.3 19.3 3.4 9.2h17.2L6.7 19.3Z"/>',
    "Grimorios": '<path d="M12 3 20 17H4ZM12 21 4 7h16Z"/><circle cx="12" cy="12" r="1" fill="currentColor"/>',
    "Thelema": '<path d="M12 3 21 12 12 21 3 12ZM5.6 5.6h12.8v12.8H5.6Z"/><circle cx="12" cy="12" r="1.6"/>',
    "Tarot": '<rect x="6.5" y="3" width="11" height="18" rx="1.2"/><circle cx="12" cy="10" r="2.4"/><path d="M12 5.2v1.6M12 13.2v1.6M7.2 10h1.6M15.2 10h1.6M9 17.5h6"/>',
    "Astrología": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.8" fill="currentColor"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1"/>',
    "Teosofía": '<path d="M17.5 4.6A9 9 0 1 0 20.6 9"/><circle cx="20.6" cy="9" r=".9" fill="currentColor"/><path d="M12 7.6 16 14.6H8Z"/>',
    "Masonería": '<path d="M12 3 6 20.5M12 3l6 17.5M6.5 11.5 12 18l5.5-6.5"/><circle cx="12" cy="3.6" r="1"/>',
    "Antroposofía": '<path d="M12 12C9 6 3 6 3 12s6 6 9 0c3-6 9-6 9 0s-6 6-9 0Z"/>',
    "Espiritismo": '<path d="M15 3.5A9 9 0 1 0 20.5 15 7.5 7.5 0 0 1 15 3.5Z"/><circle cx="17.5" cy="6.5" r=".8" fill="currentColor"/>',
    "Demonología": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="6.4"/><path d="M5.6 5.6 18.4 18.4M18.4 5.6 5.6 18.4"/><circle cx="12" cy="12" r="1.4" fill="currentColor"/>',
    "Mitología": '<circle cx="12" cy="12" r="3"/><path d="M8 5.5a7.5 7.5 0 0 0 0 13M16 5.5a7.5 7.5 0 0 1 0 13"/>',
    "Obra original": '<path d="M12 3 17 12 12 21 7 12Z"/><path d="M12 3v10"/><circle cx="12" cy="14" r="1" fill="currentColor"/>',
}
_GLIFO_DEF = '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.6" fill="currentColor"/>'

TONO = {
    "Alquimia": "#3a2f31", "Hermetismo": "#2f3840", "Cábala": "#2f3631",
    "Magia": "#35323b", "Grimorios": "#38332e", "Thelema": "#3a2e34",
    "Tarot": "#2e333d", "Astrología": "#2c3039", "Teosofía": "#35362d",
    "Masonería": "#2d3639", "Antroposofía": "#37352c", "Espiritismo": "#33343a",
    "Demonología": "#3d2c2e", "Mitología": "#353230", "Obra original": "#2c2d30",
}
_TONO_DEF = "#2a2c30"

DIAS = ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"]
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def glifo(tema):
    trazos = GLIFO.get(tema, _GLIFO_DEF)
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{trazos}</svg>'
    )


def tono(tema):
    return TONO.get(tema, _TONO_DEF)


def money(n):
    """Importe en formato argentino: $18.500 o $18.500,50 (los centavos
    solo aparecen cuando los hay)."""
    n = round(n or 0, 2)
    signo = "-" if n < 0 else ""
    texto = f"{abs(n):,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    if texto.endswith(",00"):
        texto = texto[:-3]
    return signo + "$" + texto


_MILES_CON_PUNTO = re.compile(r"^\d{1,3}(\.\d{3})+$")


def importe(valor):
    """Convierte lo que escribe una persona (o una celda de Excel) en un
    importe con hasta dos decimales. Entiende el formato argentino:
    "$15.000" -> 15000, "15.000,50" -> 15000.5, "15000,5" -> 15000.5, y
    también "15000.5" (lo que manda un <input type=number>).
    Devuelve None si no hay un número. Los importes enteros quedan int."""
    if valor is None or isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        numero = float(valor)
    else:
        texto = str(valor).strip().replace("$", "").replace(" ", "").replace("\u00a0", "")
        if not texto:
            return None
        if "," in texto and "." in texto:
            # el último separador es el decimal: 15.000,50 o 15,000.50
            if texto.rfind(",") > texto.rfind("."):
                texto = texto.replace(".", "").replace(",", ".")
            else:
                texto = texto.replace(",", "")
        elif "," in texto:
            texto = texto.replace(",", ".")          # coma decimal argentina
        elif _MILES_CON_PUNTO.match(texto):
            texto = texto.replace(".", "")           # 15.000 / 1.250.000
        try:
            numero = float(texto)
        except ValueError:
            return None
    if numero != numero or numero in (float("inf"), float("-inf")):
        return None
    numero = round(numero, 2)
    return int(numero) if numero == int(numero) else numero


def precio_o_consultar(libro):
    return money(libro["precio"]) if libro["precio"] and libro["precio"] > 0 else "Consultar"


def fecha_corta(fecha_iso):
    try:
        x = date.fromisoformat(fecha_iso)
    except (TypeError, ValueError):
        return str(fecha_iso or "")
    return f"{DIAS[(x.weekday() + 1) % 7]} {x.day} {MESES[x.month - 1]}"


def ficha(nro):
    return f"Nº {int(nro or 0):03d}"


def ficha_turno(nro):
    return f"T-{int(nro or 0):03d}"


def hoy_argentina():
    try:
        return datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).date()
    except Exception:
        return date.today()


def estado_local():
    ahora = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
    dia_semana = (ahora.weekday() + 1) % 7  # 0=domingo ... 6=sábado, como en JS
    cerrado_hoy = dia_semana in (0, 2)  # domingo y martes
    hora = ahora.hour + ahora.minute / 60
    abierto = (not cerrado_hoy) and 14 <= hora < 19
    if abierto:
        texto = "Abierto ahora · cierra a las 19"
    elif cerrado_hoy:
        texto = "Hoy cerrado"
    else:
        texto = "Cerrado · abre a las 14"
    return {"abierto": abierto, "texto": texto}


def texto_post_instagram(libro):
    lineas = []
    if libro["vendido"]:
        lineas.append("VENDIDO")
    titulo_autor = libro["titulo"] + (f" - {libro['autor']}" if libro["autor"] else "")
    lineas += [titulo_autor, ""]
    edicion = ", ".join(x for x in [libro["editorial"], str(libro["anio"] or ""), libro["pais"]] if x)
    lineas.append(edicion + ".")
    formato = ", ".join(x for x in [libro["tapa"], f"{libro['paginas']} páginas" if libro["paginas"] else ""] if x)
    if formato:
        lineas.append(formato + ".")
    if libro["ilustrado"]:
        lineas.append("Ilustrado.")
    if libro["nota"]:
        lineas.append(libro["nota"].rstrip(".") + ".")
    lineas.append(libro["estado"] + ".")
    lineas.append("Envíos a todo el país.")
    lineas.append("")
    if libro["precio"] and libro["precio"] > 0:
        lineas.append(money(libro["precio"]))
    else:
        lineas.append("Precio a consultar por privado.")
    return "\n".join(lineas)


def _entero_o_none(valor):
    numero = importe(valor)
    return None if numero is None else int(numero)


def clave_libro(titulo, autor="", editorial=""):
    """Clave para detectar libros repetidos: título + autor + editorial, sin
    importar mayúsculas, tildes ni espacios de más. Dos ediciones distintas
    del mismo libro (otra editorial) no cuentan como repetidas."""
    import unicodedata

    def normal(texto):
        texto = unicodedata.normalize("NFKD", str(texto or "").casefold())
        texto = "".join(c for c in texto if not unicodedata.combining(c))
        return " ".join(texto.split())

    return (normal(titulo), normal(autor), normal(editorial))


def es_fila_de_ejemplo(titulo):
    """Las filas de muestra de la plantilla empiezan con "(EJEMPLO)"."""
    return str(titulo or "").strip().upper().startswith("(EJEMPLO)")


def fila_planilla_a_libro(valores):
    """Convierte una fila de la planilla de importación (14 columnas, en el
    orden de scripts/generar_plantilla_catalogo.py) en un dict listo para
    basedatos.crear_libro. Devuelve None si no hay título (fila vacía).
    Ejemplares va al final para que las planillas viejas de 13 columnas
    sigan sirviendo: si está vacío, se toma 1."""
    columnas = (list(valores) + [None] * 14)[:14]
    (titulo, autor, editorial, anio, pais, tapa, paginas, tema, tipo,
     estado, precio, ilustrado, nota, ejemplares) = columnas

    titulo = str(titulo).strip() if titulo else ""
    if not titulo:
        return None

    ilustrado_texto = str(ilustrado or "").strip().lower()

    return {
        "titulo": titulo,
        "autor": str(autor or "").strip(),
        "editorial": str(editorial or "").strip(),
        "anio": _entero_o_none(anio),
        "pais": str(pais or "Argentina").strip() or "Argentina",
        "tapa": str(tapa or "").strip() or TAPAS[0],
        "paginas": _entero_o_none(paginas),
        "tema": str(tema or "").strip() or TEMAS[0],
        "tipo": str(tipo or "").strip() or TIPOS[0],
        "estado": str(estado or "").strip() or ESTADOS[0],
        "precio": max(0, importe(precio) or 0),
        "ilustrado": 1 if ilustrado_texto in ("sí", "si", "true", "1") else 0,
        "nota": str(nota or "").strip(),
        "ejemplares": max(0, _entero_o_none(ejemplares) if _entero_o_none(ejemplares) is not None else 1),
    }


def fecha_valida(texto):
    """True si es una fecha AAAA-MM-DD real (lo que manda <input type=date>)."""
    try:
        date.fromisoformat(texto)
        return len(texto) == 10
    except (TypeError, ValueError):
        return False


def hora_valida(texto):
    """True si es una hora HH:MM entre 00:00 y 23:59."""
    try:
        datetime.strptime(texto, "%H:%M")
        return len(texto) == 5
    except (TypeError, ValueError):
        return False


def mensaje_consulta_instagram(libro):
    precio = precio_o_consultar(libro)
    autor = f" de {libro['autor']}" if libro["autor"] else ""
    return f'Hola Azoth, me interesa "{libro["titulo"]}"{autor} ({precio}). ¿Sigue disponible?'
