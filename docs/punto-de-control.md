<!-- PUNTO-DE-CONTROL -->
**Tarea actual:** sobre la app Flask + SQLite ya armada y probada, se
agregaron tres pedidos: (1) soporte para varias cuentas de Instagram
configurables en vez de una sola (etiqueta + usuario, con alta/baja desde
Configuración), (2) plantilla de Excel (`scripts/generar_plantilla_catalogo.py`
→ `app/static/plantillas/azoth-catalogo-plantilla.xlsx`) con listas
desplegables por columna, y un importador por lote en
**Catálogo → Importar planilla** que crea un libro por fila con título.
Probado de punta a punta (descarga de plantilla, llenado con openpyxl,
subida, verificación de que los libros quedan cargados con tildes
correctas; alta y baja de cuentas de Instagram). Datos de prueba y
contraseña temporal borrados; `instance/` queda vacía.

**Próximo paso:** ninguno pedido explícitamente. Pendiente de decisión de
Marcos: si commitea y pushea estos cambios (no se hizo automático, por
regla del método — commitear solo cuando se pide).

**Bloqueos:** ninguno.

**Archivos en curso:** ninguno a medio terminar.

**Preguntas abiertas:**
- ¿Instagram y WhatsApp reales de Azoth para cargarlos en Configuración
  (hoy la base arranca sin ninguna cuenta cargada)?
- ¿Dónde va a vivir la PC "servidor" en el local? (sigue abierto de la
  sesión anterior)
<!-- /PUNTO-DE-CONTROL -->
