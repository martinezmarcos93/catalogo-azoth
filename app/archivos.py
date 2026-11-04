"""Portadas y PDFs de los libros, guardados en disco (instance/archivos/).

Los archivos no van a la base: la base guarda solo el nombre. El nombre lo
arma el sistema (id del libro + sufijo al azar), nunca se usa el nombre
que trae el archivo subido, y el tipo se reconoce por el contenido (los
primeros bytes), no por la extensión: un .exe renombrado a .jpg se rechaza.
"""
import logging
import secrets
from pathlib import Path

from flask import current_app

logger = logging.getLogger(__name__)

MAX_PORTADA = 15 * 1024 * 1024    # 15 MB: alcanza para una foto de celular
MAX_PDF = 150 * 1024 * 1024       # 150 MB: un libro escaneado entero

TIPOS_PORTADA = {"jpg": "image/jpeg", "png": "image/png", "webp": "image/webp"}


class ArchivoInvalido(ValueError):
    """El archivo subido no es del tipo esperado o es demasiado grande."""


def carpeta():
    ruta = Path(current_app.config["ARCHIVOS"])
    ruta.mkdir(parents=True, exist_ok=True)
    return ruta


def _tipo_imagen(cabecera):
    if cabecera.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if cabecera.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if cabecera[:4] == b"RIFF" and cabecera[8:12] == b"WEBP":
        return "webp"
    return None


def _tamanio(archivo):
    archivo.stream.seek(0, 2)
    tamanio = archivo.stream.tell()
    archivo.stream.seek(0)
    return tamanio


def hay_archivo(archivo):
    """True si en el formulario vino un archivo de verdad (no el campo vacío)."""
    return archivo is not None and bool(archivo.filename)


def validar_portada(archivo):
    """Devuelve la extensión ('jpg', 'png', 'webp') o lanza ArchivoInvalido."""
    tipo = _tipo_imagen(archivo.stream.read(16))
    archivo.stream.seek(0)
    if tipo is None:
        raise ArchivoInvalido("La portada tiene que ser una foto JPG, PNG o WEBP.")
    if _tamanio(archivo) > MAX_PORTADA:
        raise ArchivoInvalido("La foto de portada pesa más de 15 MB.")
    return tipo


def validar_pdf(archivo):
    """Devuelve 'pdf' o lanza ArchivoInvalido."""
    cabecera = archivo.stream.read(1024)
    archivo.stream.seek(0)
    if b"%PDF-" not in cabecera:
        raise ArchivoInvalido("El archivo no es un PDF.")
    if _tamanio(archivo) > MAX_PDF:
        raise ArchivoInvalido("El PDF pesa más de 150 MB.")
    return "pdf"


def crear_archivo(libro_id, tipo, extension, archivo):
    """Guarda el archivo ya validado y devuelve el nombre con que quedó.
    tipo es 'portada' o 'pdf'. El sufijo al azar hace que cada versión
    tenga un nombre nuevo, así el navegador no muestra una portada vieja."""
    nombre = f"{libro_id}-{tipo}-{secrets.token_hex(4)}.{extension}"
    archivo.save(carpeta() / nombre)
    return nombre


def obtener_ruta_archivo(nombre):
    """Ruta en disco de un archivo guardado, o None si no existe."""
    if not nombre or "/" in nombre or "\\" in nombre or nombre.startswith("."):
        return None
    ruta = carpeta() / nombre
    return ruta if ruta.is_file() else None


def eliminar_archivo(nombre):
    ruta = obtener_ruta_archivo(nombre)
    if ruta is None:
        return
    try:
        ruta.unlink()
    except OSError as e:
        logger.error("no se pudo borrar el archivo %s: %s", ruta, e, exc_info=True)
