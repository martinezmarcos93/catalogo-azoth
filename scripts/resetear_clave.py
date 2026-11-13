"""Cambia la contraseña de Azoth cuando Silvio se la olvidó.

No borra ningún dato: solo reemplaza la contraseña guardada.
Se corre en la PC del local (no hace falta cerrar el sistema):

    python scripts/resetear_clave.py
o doble clic en scripts/windows/resetear-clave.bat
"""
import getpass
import sqlite3
import sys
from pathlib import Path

from werkzeug.security import generate_password_hash

RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / "instance" / "azoth.db"


def resetear_clave(ruta_base, clave_nueva):
    if len(clave_nueva) < 8:
        raise ValueError("La contraseña tiene que tener al menos 8 caracteres.")
    if not Path(ruta_base).exists():
        raise FileNotFoundError(f"No encontré la base en {ruta_base}")
    conexion = sqlite3.connect(ruta_base)
    try:
        with conexion:
            cursor = conexion.execute(
                "UPDATE usuario SET clave_hash = ? WHERE id = 1",
                (generate_password_hash(clave_nueva),),
            )
        return cursor.rowcount == 1
    finally:
        conexion.close()


if __name__ == "__main__":
    print("Cambiar la contraseña de Azoth (los libros, ventas y turnos no se tocan).\n")
    clave = getpass.getpass("Contraseña nueva: ")
    if clave != getpass.getpass("Repetila: "):
        sys.exit("Las dos contraseñas no coinciden. No se cambió nada.")
    try:
        if resetear_clave(BASE, clave):
            print("Listo: ya se puede entrar con la contraseña nueva.")
        else:
            print("Todavía no hay usuario: al abrir el sistema va a pedir crear la contraseña.")
    except (ValueError, FileNotFoundError) as e:
        sys.exit(str(e))
