"""Arranca Azoth en la red local.

Uso:
    python run.py

Silvio entra desde la PC en http://localhost:5000 y desde el celular
(conectado al mismo WiFi) en http://<IP de esta PC>:5000 — la IP se
imprime abajo al arrancar.
"""
import socket

from app import create_app

app = create_app()


def _ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    ip = _ip_local()
    print("\n  Azoth está corriendo.")
    print(f"  En esta PC:      http://localhost:5000")
    print(f"  Desde el celular: http://{ip}:5000  (mismo WiFi)\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
