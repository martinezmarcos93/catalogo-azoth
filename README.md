# Azoth · Sistema de gestión

Catálogo de libros, vitrina online, ventas, turnos de tatuaje y calculadora
de costos para Azoth (librería esotérica y salón de tatuajes de Silvio
Abadía — "Silvio Caveira" en redes —, Bolívar 1447, San Telmo). Pensado para que lo use una sola persona
(Silvio) desde la PC del local y desde el celular.

## Stack

- Python 3 + Flask, sin ORM: SQLite directo con verbos en español
  (`crear_libro`, `listar_ventas`, `actualizar_turno`, etc. en `app/basedatos.py`).
- Server-rendered con Jinja2: cada pantalla es una página real, sin
  JavaScript de estado — los diálogos (`<dialog>` nativo) y el autocompletado
  de precio son el único JS de la app, todo inline y mínimo.
- Un solo usuario, login con contraseña hasheada (Werkzeug), sesión por cookie.
- PWA: instalable en el celular como ícono de pantalla de inicio
  (`manifest.json` + `sw.js`, que solo cachea CSS/imágenes, nunca datos).

## Instalación

**En la PC del local (Windows): seguir [`docs/instalacion-windows.md`](docs/instalacion-windows.md)**
— instalación paso a paso, arranque automático, celular, backup, restauración
y actualización, con los `.bat` de `scripts/windows/`.

Instalación manual (para desarrollo):

```bash
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Uso

```bash
.venv\Scripts\python.exe run.py
```

La consola imprime la IP de la PC. La primera vez que se abre, el sistema
pide crear una contraseña (Primer ingreso) — de ahí en más es la única
forma de entrar. La contraseña se puede cambiar después desde
**Configuración → Cambiar contraseña**.

- **En la PC del local:** `http://localhost:5000`
- **Desde el celular de Silvio:** mismo WiFi que la PC → `http://<IP de la PC>:5000`
  (la IP la imprime la consola al arrancar). En Chrome/Android, menú →
  "Instalar app" o "Agregar a pantalla de inicio" para que quede como un
  ícono más, igual que una app.

### Si Windows bloquea la conexión desde el celular

Windows puede tener el firewall cerrado para conexiones entrantes. Si el
celular no carga la página aunque esté en el mismo WiFi:

1. Panel de control → Firewall de Windows Defender → Configuración avanzada.
2. Reglas de entrada → Nueva regla → Puerto → TCP 5000 → Permitir la conexión.

## Tests

```bash
.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
```

(En Linux/macOS: `.venv/bin/python -m unittest discover -s tests -t . -v`.)
Usan una base temporal: no tocan `instance/azoth.db`.

## Ejemplares (stock) y ventas

- Cada libro tiene **Ejemplares en stock** (por defecto 1). Cada venta
  descuenta uno; si no quedan ejemplares, la venta no se registra.
- Al vender el **último** ejemplar el libro pasa a VENDIDO, sale de la
  Vitrina y queda el aviso pendiente de marcar VENDIDO en el post.
  Si se repone (editar el libro y subir los ejemplares) vuelve a la Vitrina.
- **Un libro con ventas no se puede borrar**: las ventas son el registro
  histórico. El botón Eliminar solo aparece en libros que nunca se vendieron.
- Eliminar una venta es **anularla** (para corregir una carga por error):
  el ejemplar vuelve al estante.
- Las bases creadas antes de esta función se actualizan solas al arrancar:
  los libros vendidos quedan con 0 ejemplares y el resto con 1.

## Datos

Todo vive en la carpeta `instance/` (no se sube al repositorio):
`azoth.db` (SQLite) y `archivos/` (portadas y PDFs). **Para hacer backup hay
que copiar la carpeta `instance/` entera**: copiar solo la base deja afuera
las portadas y los PDFs. `python scripts/crear_backup.py [destino]` lo hace
solo (copia segura de la base aunque el sistema esté abierto + archivos);
en Windows, `scripts/windows/backup-azoth.bat`. La base arranca vacía.

### Portadas y PDF de cada libro

Al cargar o editar un libro se puede subir:

- **Portada**: foto JPG, PNG o WEBP, hasta 15 MB (desde el celular se puede
  sacar la foto en el momento). Reemplaza al dibujo del tema en el Catálogo,
  la Vitrina y el Panel.
- **PDF del libro**: hasta 150 MB. Es de uso interno: aparece como botón
  "PDF" en el Catálogo, nunca en la Vitrina.

El tipo de archivo se reconoce por su contenido, no por la extensión. Los
archivos se sirven solo con la sesión iniciada. Subir uno nuevo reemplaza
(y borra) el anterior; en Editar también se pueden quitar. Al borrar un
libro se borran sus archivos.

### Cargar el catálogo por lote (planilla Excel)

Desde **Catálogo → Importar planilla**:

1. Descargar la plantilla (`.xlsx`, con listas desplegables para Tapa,
   Tema, Tipo, Estado e Ilustrado, para que no se pueda escribir un valor
   que el sistema no reconozca).
2. Completar un libro por fila y borrar las 2 filas de ejemplo. La última
   columna, **Ejemplares**, es cuántas copias hay (vacía = 1); las planillas
   viejas sin esa columna se siguen pudiendo importar.
3. Subir el archivo: cada fila con título se agrega como libro nuevo
   (no reemplaza lo que ya estaba cargado, así que importar la misma
   planilla dos veces duplica los libros).

Si cambian las columnas (`TEMAS`, `TIPOS`, `ESTADOS`, `TAPAS` en
`app/utilidades.py`), hay que volver a generar la plantilla con
`python scripts/generar_plantilla_catalogo.py`.

## Redes sociales

Desde **Configuración** se puede cargar más de una cuenta de Instagram
(por ejemplo, una para la librería y otra para tatuajes), cada una con su
etiqueta. La primera de la lista es la que usan la Vitrina y el botón
"Consultar por Instagram" de cada libro.

Vienen precargadas las cuentas reales (`app/basedatos.py`): @azothlibreria
(librería, la de la Vitrina), @solarestudioba (tatuajes) y @silviocaveira,
más el WhatsApp +54 9 11 3786-9154. Se pueden cambiar o borrar desde
Configuración; si se borran todas, no vuelven a aparecer solas.

## Qué significa "contraseña configurable"

No hay usuarios ni roles: es un sistema de una sola persona. La contraseña
no está en ningún archivo de configuración ni variable de entorno — la
elige Silvio la primera vez que abre el sistema y la cambia él mismo
cuando quiera, sin tocar código.

## Limitaciones conocidas (a propósito, por simplicidad)

- **Solo funciona en la red local del negocio.** El celular tiene que estar
  conectado al mismo WiFi que la PC donde corre el servidor. No hay acceso
  desde afuera del local ni desde datos móviles.
- **Instalación como PWA completa (con ícono propio y sin barra del
  navegador) depende del navegador y de que la conexión sea `https` o
  `localhost`.** Sobre `http://<IP>` en la red local, la mayoría de los
  navegadores igual permiten "agregar a pantalla de inicio", pero puede
  aparecer con la barra de direcciones visible en vez de a pantalla
  completa. Si en algún momento se necesita el ícono completo sin barra,
  o acceso desde cualquier lado (no solo el WiFi del local), el camino más
  simple sin exponer la PC a internet es un **Cloudflare Tunnel**: HTTPS
  gratis, acceso desde cualquier conexión, y los datos siguen viviendo
  únicamente en la PC del local.
- El estado "abierto ahora / cerrado" del Panel asume el horario fijo
  martes y domingo cerrado, 14 a 19 h. Si el horario cambia de forma
  permanente, hay que tocar `app/utilidades.py::estado_local`.

## Estructura

```
app/
  __init__.py        fábrica de la app, registra blueprints y filtros Jinja
  auth.py            login, primer ingreso, logout
  archivos.py        portadas y PDFs en disco: validación por contenido, guardado y borrado
  basedatos.py        capa de datos (sqlite3 directo, verbos en español)
  rutas.py            todas las vistas: panel, catálogo, vitrina, ventas, turnos, calculadora, configuración
  utilidades.py        formato de moneda/fecha, glifos y tonos por tema, texto de posts de Instagram
  schema.sql          esquema de la base (las migraciones de bases viejas están en basedatos._migrar)
  templates/           Jinja2 (una plantilla por pantalla + _macros.html + _form_libro.html)
  static/
    css/               el sistema de diseño (7 archivos: tokens, tipografía, superficies, navegación, controles, datos, ornamentación)
    img/logo-azoth.png
    icons/             íconos de la PWA, generados a partir del logo
    plantillas/        azoth-catalogo-plantilla.xlsx, para la carga por lote
    manifest.json, sw.js
tests/
  test_app.py         tests de punta a punta (unittest, sin dependencias extra)
scripts/
  crear_backup.py      backup de instance/ (base con la API de backup de SQLite + archivos)
  windows/             instalar-azoth.bat, iniciar-azoth.bat, backup-azoth.bat
  generar_plantilla_catalogo.py   regenera la plantilla de Excel si cambian las columnas
instance/              azoth.db + archivos/ (portadas y PDFs) + clave secreta de sesión — nada de esto se versiona
legado/                 el artefacto HTML de un solo archivo de la versión anterior, como referencia
```

## Próximos pasos posibles

- Cloudflare Tunnel si se necesita acceso fuera del WiFi del local
  (antes, cerrar la redirección abierta del login: hoy acepta `siguiente=//otro-sitio`).
- Achicar las fotos de portada al subirlas (hoy se guardan tal cual; con
  muchos libros y fotos de celular, el catálogo puede cargar lento en el
  teléfono). Requiere Pillow → pasar antes por dependency-auditor.
- Hacer configurable el horario que usa el cálculo de "abierto ahora".
