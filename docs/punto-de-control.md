<!-- PUNTO-DE-CONTROL -->
**Tarea actual:** main con todo lo del 03-nov: ejemplares por libro, borrado
protegido, validación de turnos, portada y PDF, arreglos de UI (botón
Eliminar, portada en el panel), instructivo de instalación en Windows
(`docs/instalacion-windows.md`) con `.bat` de instalar/iniciar/backup y
`scripts/crear_backup.py` (backup seguro de instance/). 29 tests OK.

**Próximo paso:** instalar en la PC del local siguiendo
`docs/instalacion-windows.md`. Los `.bat` no se probaron en Windows real:
verificarlos ahí.

**Ideas futuras (Marcos, 03-nov):**
- Que Silvio la use en su Android como una app más, sin APK: ya es PWA →
  "Agregar a pantalla de inicio" (como Tonus/Ikigai en iPhone). Pantalla
  completa y uso fuera del WiFi del local → Cloudflare Tunnel (HTTPS).
- Controlar Spotify desde el sistema (para después; la API pide Premium e internet).

**Bloqueos:** ninguno.

**Preguntas abiertas:**
- Vista de celular sin probar. ¿El PDF es solo para Silvio o se vende?
- Etiquetas de Instagram: confirmar. Achicar fotos (Pillow → dependency-auditor).
- Login: redirección abierta `siguiente=//...` (cerrar antes de un Tunnel).
<!-- /PUNTO-DE-CONTROL -->
