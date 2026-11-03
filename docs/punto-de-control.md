<!-- PUNTO-DE-CONTROL -->
**Tarea actual:** reescribir Azoth de artefacto HTML (localStorage, un solo
archivo) a app Flask + SQLite real, con login propio para Silvio, redes
sociales configurables y calculadora de costos. Hecho y probado de punta a
punta con requests HTTP reales (primer ingreso, catálogo, ventas, turnos,
calculadora, cambio de contraseña, manifest/service worker). Base de datos
de prueba borrada; queda vacía para el primer uso real.

**Próximo paso:** que Marcos decida si quiere `git init` + primer commit
(no lo hice porque no se pidió explícitamente). Después, cuando Silvio
tenga su catálogo en Excel, armar el importador (mencionado como pendiente
en el README, no implementado).

**Bloqueos:** ninguno. El acceso desde el celular depende de que la PC de
Silvio y su celular estén en el mismo WiFi y de que el firewall de Windows
deje pasar el puerto 5000 (instrucciones en el README).

**Archivos en curso:** ninguno a medio terminar — todo lo descripto en el
README está escrito y probado.

**Preguntas abiertas:**
- ¿Dónde va a vivir la PC "servidor" en el local — la misma PC de Silvio
  para catálogo, o una exclusiva? Afecta si conviene un acceso directo que
  arranque `run.py` solo al prender la PC.
- ¿Instagram y WhatsApp reales de Azoth para cargarlos en Configuración
  (hoy están en blanco/con el default `azothlibreria`)?
<!-- /PUNTO-DE-CONTROL -->
