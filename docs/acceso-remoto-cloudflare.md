# Acceso desde cualquier lado (Cloudflare Tunnel + dominio gratis)

> **Estado (12-nov-2026): postergado.** La entrega es solo en red local. Se
> creó una cuenta en DigitalPlat (`mmac.dev.lab@gmail.com`) y
> `azothlibreria.dpdns.org` estaba libre, pero el cupo gratis exige
> verificar la cuenta con GitHub (vinculándolo en DigitalPlat → /kyc) y no
> se completó. El código ya está preparado para exponerse (seguridad del
> login hecha).

Con esto Silvio entra al sistema desde el celular **con WiFi o con datos,
donde esté**, con una dirección fija con candado (HTTPS), por ejemplo
`https://azoth.dpdns.org`. También la puede usar en la PC.

**Cómo funciona:** un programita (`cloudflared`) corre en la PC del local y
abre una conexión de salida hacia Cloudflare. Cloudflare recibe las visitas
a la dirección y las pasa por ese camino hasta el sistema. Los datos siguen
viviendo solo en la PC: **si la PC está apagada, el celular no ve nada**.
No hay que tocar el router ni abrir puertos.

**Seguridad:** el sistema queda en internet protegido por la contraseña
(mínimo 8 caracteres; después de 5 intentos fallidos el login se bloquea
5 minutos). Opcional, más adelante: Cloudflare Access (paso 7).

---

## Parte A — Marcos, desde casa (antes del sábado)

### 1. Registrar el dominio gratis (DigitalPlat)

1. Entrar a <https://dash.domain.digitalplat.org> y crear una cuenta.
2. Registrar el nombre. **Solo se permite un dominio por cuenta**: elegirlo
   bien. Sugerencias: `azoth.dpdns.org`, `azothlibreria.dpdns.org`
   (también hay `.us.kg`, `.xx.kg`, `.qd.je`, `.qzz.io`).
3. Fijarse en el panel **si el dominio vence y cada cuánto se renueva**, y
   anotarlo en el calendario: si vence, el acceso remoto deja de andar (el
   sistema en el local sigue funcionando igual).
4. Todavía **no** tocar los nameservers: primero hacen falta los de Cloudflare.

### 2. Cargar el dominio en Cloudflare

1. Elegir la cuenta de Cloudflare. Recomendado: **una cuenta nueva solo para
   Azoth** (mail tuyo o de Azoth), así no se mezcla con Ikigai ni MMAC y se
   le puede pasar a Silvio algún día.
2. **Add a domain** → escribir el dominio completo (`azoth.dpdns.org`) →
   plan **Free**.
3. Cloudflare muestra **dos nameservers** (algo como
   `ana.ns.cloudflare.com` y `bob.ns.cloudflare.com`). Copiarlos tal cual.
4. Volver a DigitalPlat → el dominio → **Nameservers** → pegar los dos →
   guardar.
5. Esperar el mail de Cloudflare "dominio activo" (de minutos a 48 h). Se
   puede comprobar desde Linux con `dig NS azoth.dpdns.org +short`: tienen
   que aparecer los de Cloudflare.

### 3. Crear el túnel

1. En Cloudflare: **Zero Trust** (menú izquierdo). Si pide elegir plan,
   **Free**.
2. **Networks → Tunnels → Create a tunnel** → tipo **Cloudflared** →
   nombre `azoth-local` → Save.
3. En "Install and run a connector" elegir **Windows**. Aparece un comando
   que termina con un **token** largo. **Copiarlo a un lugar seguro** (es la
   llave del túnel: no mandarlo por WhatsApp ni subirlo a GitHub).
4. **Public Hostname** (siguiente paso del asistente):
   - Subdomain: vacío · Domain: `azoth.dpdns.org`
   - Service: Type **HTTP** · URL **`localhost:5000`**
   - Save tunnel.
5. En el dominio → **SSL/TLS → Edge Certificates** → activar **Always Use
   HTTPS**.

## Parte B — En el local, el sábado (después de instalar el sistema)

### 4. Instalar cloudflared en la PC de Silvio

1. Bajar el instalador de Windows (`cloudflared-windows-amd64.msi`) desde
   <https://github.com/cloudflare/cloudflared/releases/latest> e instalarlo.
2. Abrir **Símbolo del sistema como administrador** (Inicio → escribir
   `cmd` → clic derecho → Ejecutar como administrador).
3. Pegar el comando del paso 3.3, que tiene esta forma:
   `cloudflared.exe service install <TOKEN>`
4. Queda instalado como **servicio de Windows**: arranca solo al prender la
   PC, sin ventana. En Cloudflare → Tunnels, `azoth-local` tiene que pasar a
   **HEALTHY**.

### 5. Probar

1. Con `iniciar-azoth.bat` abierto, en el celular **con datos (WiFi
   apagado)**: abrir `https://azoth.dpdns.org` → tiene que aparecer el login.
2. Entrar con la contraseña y cargar algo de prueba; verlo en la PC; borrarlo.
3. En Chrome del celular: menú ⋮ → **Instalar app** / "Agregar a la
   pantalla principal". Con HTTPS queda como app a pantalla completa.

### 6. Qué dirección usar

| Dónde | Dirección |
|---|---|
| En la PC del local | `http://localhost:5000` (anda aunque se corte internet) |
| Celular, en cualquier lado | `https://azoth.dpdns.org` |

## Mantenimiento y problemas

| Qué pasa | Qué hacer |
|---|---|
| El celular no carga desde afuera | ¿PC prendida? ¿ventana negra abierta? ¿internet en el local? En Cloudflare → Tunnels, ¿`azoth-local` está HEALTHY? |
| Error 502 / "Bad gateway" | El túnel anda pero el sistema no: abrir `iniciar-azoth.bat`. |
| Tunnel "DOWN" | En la PC: Servicios de Windows → `Cloudflared agent` → Iniciar. |
| "Demasiados intentos fallidos" | Esperar 5 minutos. Si se olvidó la clave: `resetear-clave.bat`. |
| Cambiar de PC | Instalar el sistema y cloudflared con el **mismo token** en la nueva; desinstalar en la vieja (`cloudflared.exe service uninstall`). |
| Sospecha de que el token se filtró | Cloudflare → Tunnels → `azoth-local` → borrar y crear otro; reinstalar con el token nuevo. |

### 7. Opcional: segunda llave con Cloudflare Access

Zero Trust → Access → Applications → Add → Self-hosted → dominio
`azoth.dpdns.org` → política "Allow" con el mail de Silvio. Antes del login
del sistema, Cloudflare le pide el mail y le manda un código. Más seguro,
pero un paso más cada tanto: decidirlo con Silvio.
