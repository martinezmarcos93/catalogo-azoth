<!-- PUNTO-DE-CONTROL -->
**Tarea actual:** rama `feat/ejemplares-y-turnos` (sin commitear): (1) stock por
libro (`ejemplares`): cada venta descuenta uno, sin stock no se vende, al
agotarse queda VENDIDO + aviso de Instagram; anular una venta devuelve el
ejemplar; migración automática de bases viejas. (2) Un libro con ventas no
se puede borrar (antes daba error 500). (3) Turnos: se valida fecha y hora
al crear y editar; una fecha rota guardada ya no rompe la pantalla.
(4) WhatsApp y 3 cuentas de Instagram reales precargadas por defecto.
(5) Plantilla de Excel con columna Ejemplares al final. (6) Primera suite
de tests: `tests/test_app.py`, 18 tests OK.

**Próximo paso:** que Marcos revise el diff y decida commit + merge a main.
Después: instalar en la PC del local (Windows).

**Bloqueos:** ninguno.

**Archivos en curso:** ninguno a medio terminar.

**Preguntas abiertas:**
- Etiquetas de las cuentas de Instagram ("Librería", "Tatuajes · Solar
  Estudio", "Silvio"): confirmar con Marcos/Silvio.
- ¿Dónde va a vivir la PC "servidor" en el local?
- Login: redirección abierta con `siguiente=//...` (irrelevante en LAN;
  cerrar antes de un Cloudflare Tunnel).
<!-- /PUNTO-DE-CONTROL -->
