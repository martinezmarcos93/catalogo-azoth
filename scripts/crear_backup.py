"""Crea un backup completo de Azoth: base de datos, portadas/PDFs y clave de sesión.

La base se copia con la función de backup de SQLite, así que se puede
correr con el sistema abierto sin que la copia salga corrupta.

Uso:
    python scripts/crear_backup.py                  -> Documentos/Backups-Azoth
    python scripts/crear_backup.py E:\\             -> a un pendrive
Crea una carpeta nueva por backup: azoth-backup-AAAA-MM-DD_HHMM.
"""
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
INSTANCE = RAIZ / "instance"


def crear_backup(destino_base):
    if not (INSTANCE / "azoth.db").exists():
        raise SystemExit(f"No encontré la base en {INSTANCE / 'azoth.db'}: ¿el sistema ya se usó alguna vez?")
    destino = Path(destino_base) / f"azoth-backup-{datetime.now():%Y-%m-%d_%H%M}"
    destino.mkdir(parents=True, exist_ok=False)

    origen = sqlite3.connect(INSTANCE / "azoth.db")
    copia = sqlite3.connect(destino / "azoth.db")
    with copia:
        origen.backup(copia)
    origen.close()
    copia.close()

    if (INSTANCE / "archivos").is_dir():
        shutil.copytree(INSTANCE / "archivos", destino / "archivos")
    if (INSTANCE / "clave_secreta.txt").exists():
        shutil.copy2(INSTANCE / "clave_secreta.txt", destino / "clave_secreta.txt")

    cantidad = sum(1 for _ in (destino / "archivos").glob("*")) if (destino / "archivos").is_dir() else 0
    return destino, cantidad


if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else Path.home() / "Documents" / "Backups-Azoth"
    destino, cantidad = crear_backup(base)
    print(f"Backup listo: {destino}")
    print(f"  base de datos + {cantidad} archivos (portadas y PDFs)")
