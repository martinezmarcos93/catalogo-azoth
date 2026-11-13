# Instalar Azoth en la PC del local (Windows)

Instructivo para dejar el sistema andando en la PC de Silvio y que lo use
también desde el celular. Lleva unos 20 minutos. Hace falta internet solo
durante la instalación.

## Antes de ir

- [ ] Descargar el sistema: en GitHub (`martinezmarcos93/catalogo-azoth`,
      rama `main`) → **Code → Download ZIP**. Llevarlo en un pendrive.
- [ ] Llevar el celular de Silvio a mano (o que esté en el local).
- [ ] Saber la clave del WiFi del local y, si se puede, del router
      (para dejarle una IP fija a la PC, paso 6).

## 1. Instalar Python (una sola vez)

1. Entrar a <https://www.python.org/downloads/> y bajar la última versión de Python 3.
2. Al instalar, **tildar "Add python.exe to PATH"** abajo de todo y elegir "Install Now".

## 2. Copiar el sistema

1. Descomprimir el ZIP en `C:\Azoth` (la carpeta tiene que quedar con
   `run.py`, `app\`, `scripts\` adentro, no en una subcarpeta).
2. **No ponerlo en el Escritorio ni en OneDrive**: OneDrive sincroniza la
   base mientras se usa y la puede romper.

## 3. Instalar

Doble clic en `C:\Azoth\scripts\windows\instalar-azoth.bat`. Tarda un par
de minutos; al final dice "Listo".

## 4. Primer arranque

1. Doble clic en `C:\Azoth\scripts\windows\iniciar-azoth.bat`. Se abre una
   ventana negra que muestra dos direcciones: la de la PC y la del celular
   (anotar la del celular, algo como `http://192.168.0.15:5000`).
2. Si Windows pregunta por el **Firewall**: tildar **Redes privadas** y
   "Permitir acceso". (Si no pregunta y el celular no conecta, ver
   "Problemas" abajo.)
3. Abrir el navegador en la PC: `http://localhost:5000`.
4. Aparece **Primer ingreso**: que Silvio elija su contraseña (mínimo 8
   caracteres). No hay forma de recuperarla si se
   olvida sin tocar la base, así que conviene que la anote en un lugar seguro.
5. En **Configuración**, revisar el WhatsApp y las cuentas de Instagram
   (vienen cargadas: @azothlibreria, @solarestudioba, @silviocaveira).

**La ventana negra tiene que quedar abierta** (se puede minimizar). Si se
cierra, el sistema deja de andar en la PC y en el celular.

## 5. Que arranque solo al prender la PC

1. Tecla Windows + R → escribir `shell:startup` → Enter. Se abre una carpeta.
2. Con clic derecho sobre `iniciar-azoth.bat` → **Crear acceso directo**, y
   mover ese acceso directo a la carpeta que se abrió.
3. Clic derecho sobre el acceso directo → Propiedades → **Ejecutar: Minimizada**.

Además: Configuración de Windows → Sistema → Inicio/apagado y suspensión →
**Suspender: Nunca** (cuando está enchufada). Si la PC se suspende, el
celular no conecta.

## 6. IP fija de la PC (recomendado)

El router le puede cambiar la dirección a la PC de un día para el otro, y el
acceso del celular deja de andar. Lo más prolijo es entrar al router y
**reservar la IP** de esa PC (opción "DHCP reservation" / "IP estática" /
"Reserva de direcciones", según la marca). Si no se tiene acceso al router,
no pasa nada grave: cuando cambie, la ventana negra muestra la nueva y se
vuelve a hacer el paso 7.

## 7. El celular de Silvio (Android)

1. Conectado al **WiFi del local** (con datos móviles no anda).
2. Abrir **Chrome** y entrar a la dirección del celular que mostró la
   ventana negra (`http://192.168.x.x:5000`). Entrar con la contraseña.
3. Menú ⋮ → **"Agregar a la pantalla principal"** (o "Instalar app"). Queda
   como un ícono más, con el logo de Azoth. Puede abrirse con la barra del
   navegador visible: es normal en la red local.

### Fuera del local (no incluido en esta entrega)

Por ahora el celular funciona solo conectado al WiFi del local. Si más
adelante se quiere usar con datos, la guía está en
[`acceso-remoto-cloudflare.md`](acceso-remoto-cloudflare.md) (necesita un
dominio; el gratis de DigitalPlat pide verificar la cuenta con GitHub).

## 8. Backup

**Qué hay que guardar:** la carpeta `C:\Azoth\instance\` entera: la base
(`azoth.db`), las portadas y PDFs (`archivos\`) y la clave de sesión. Copiar
solo `azoth.db` deja afuera las fotos y los PDFs.

**Cómo:** doble clic en `C:\Azoth\scripts\windows\backup-azoth.bat`. Se
puede hacer con el sistema abierto (la base se copia de forma segura). Crea
una carpeta nueva con fecha, por ejemplo
`Documentos\Backups-Azoth\azoth-backup-2026-11-10_1830`.

**A un pendrive:** abrir una ventana de comandos en `C:\Azoth\scripts\windows`
y correr `backup-azoth.bat E:\` (cambiando `E:` por la letra del pendrive).

**Cada cuánto:** una vez por semana, y siempre antes de actualizar el
sistema. Conviene que al menos un backup viva **fuera de la PC** (pendrive,
o subir la carpeta a Drive): si la PC se rompe o se la roban, los backups
de Documentos se pierden con ella.

### Restaurar un backup

1. Cerrar la ventana negra (el sistema tiene que estar apagado).
2. Renombrar `C:\Azoth\instance` a `instance-viejo` (por las dudas).
3. Copiar la carpeta del backup y renombrarla a `C:\Azoth\instance`
   (adentro tiene que quedar `azoth.db`, `archivos\` y `clave_secreta.txt`).
4. Volver a abrir `iniciar-azoth.bat`.

## Actualizar el sistema (cuando haya una versión nueva)

1. Hacer un backup (paso 8).
2. Cerrar la ventana negra.
3. Descomprimir el ZIP nuevo **en otra carpeta**, por ejemplo `C:\Azoth-nuevo`.
4. Mover `C:\Azoth\instance` adentro de `C:\Azoth-nuevo`.
5. Renombrar `C:\Azoth` a `C:\Azoth-anterior` y `C:\Azoth-nuevo` a `C:\Azoth`.
6. Doble clic en `scripts\windows\instalar-azoth.bat` y después en `iniciar-azoth.bat`.
7. Si todo anda, después de unos días se puede borrar `C:\Azoth-anterior`.

Nunca borrar ni pisar la carpeta `instance\`: ahí están todos los datos.

## Problemas frecuentes

| Qué pasa | Qué hacer |
|---|---|
| El celular no carga la página | Mismo WiFi que la PC; la ventana negra abierta; la IP es la que muestra hoy la ventana. Si sigue sin andar: Firewall (abajo). |
| Firewall | Panel de control → Firewall de Windows Defender → Configuración avanzada → Reglas de entrada → Nueva regla → Puerto → TCP 5000 → Permitir → tildar Privado. También revisar que la red WiFi esté como **Privada** (Configuración → Red → propiedades del WiFi). |
| "No se encontró Python" | Reinstalar Python tildando "Add python.exe to PATH" y reiniciar la PC. |
| La ventana negra se cierra sola al abrir | Abrirla desde una ventana de comandos (`cd C:\Azoth` y `scripts\windows\iniciar-azoth.bat`) para ver el error, y mandarle una foto a Marcos. |
| Silvio se olvidó la contraseña | Doble clic en `scripts\windows\resetear-clave.bat` en la PC del local y escribir una nueva. No se pierde ningún dato. |
