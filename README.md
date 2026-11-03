# Azoth · Sistema de gestión

Catálogo de libros, vitrina online, ventas, turnos de tatuaje y calculadora
de costos para Azoth (librería esotérica y salón de tatuajes de Silvio
Abadía, Bolívar 1447, San Telmo). Pensado para que lo use una sola persona
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

## Datos

Todo vive en `instance/azoth.db` (SQLite, no se sube al repositorio). Para
hacer backup alcanza con copiar ese archivo. La base arranca vacía: los
libros se cargan desde **Catálogo → Cargar libro**, uno por uno, o se puede
pedir que se arme un importador desde el Excel del catálogo de Silvio
cuando esté listo (no implementado todavía).

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
  basedatos.py        capa de datos (sqlite3 directo, verbos en español)
  rutas.py            todas las vistas: panel, catálogo, vitrina, ventas, turnos, calculadora, configuración
  utilidades.py        formato de moneda/fecha, glifos y tonos por tema, texto de posts de Instagram
  schema.sql          esquema de la base
  templates/           Jinja2 (una plantilla por pantalla + _macros.html + _form_libro.html)
  static/
    css/               el sistema de diseño (7 archivos: tokens, tipografía, superficies, navegación, controles, datos, ornamentación)
    img/logo-azoth.png
    icons/             íconos de la PWA, generados a partir del logo
    manifest.json, sw.js
instance/              azoth.db (no versionado) + clave secreta de sesión (no versionada)
legado/                 el artefacto HTML de un solo archivo de la versión anterior, como referencia
```

## Próximos pasos posibles

- Importador del catálogo real desde Excel (`xlsx` + `openpyxl`/`pandas`).
- Cloudflare Tunnel si se necesita acceso fuera del WiFi del local.
- Hacer configurable el horario que usa el cálculo de "abierto ahora".
