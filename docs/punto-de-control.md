<!-- PUNTO-DE-CONTROL -->
**Tarea actual:** main al día en GitHub (`5f30dc2`): ejemplares por libro,
borrado protegido, validación de turnos, portada y PDF por libro. Ramas de
trabajo borradas. Probado en el navegador (Chrome, escritorio): login, panel,
catálogo, subida de portada desde el formulario, vitrina, ficha, PDF.
Arreglos de esa prueba, commiteados en la rama `fix/panel-y-boton-eliminar` (sin push): portada real en "Últimas ventas" del
panel; botón Eliminar ilegible (texto del mismo color que el fondo);
service worker a `azoth-estatico-v3`. 28 tests OK.

**Próximo paso:** OK de Marcos para push + merge de `fix/panel-y-boton-eliminar` a main; instalar en la PC del local (Windows).

**Ideas futuras (Marcos, 03-nov):**
- Que Silvio la use en su Android como una app más, sin APK: ya es PWA →
  "Agregar a pantalla de inicio" (como Tonus/Ikigai en iPhone). Pantalla
  completa y uso fuera del WiFi del local → Cloudflare Tunnel (HTTPS).
- Controlar Spotify desde el sistema (para después; la API pide Premium e internet).

**Bloqueos:** ninguno.

**Archivos en curso:** ninguno a medio terminar.

**Preguntas abiertas:**
- Vista de celular sin probar (la ventana de Chrome no se pudo achicar).
- ¿El PDF es solo para Silvio o algún día se vende/entrega al cliente?
- Etiquetas de Instagram ("Librería", "Tatuajes · Solar Estudio", "Silvio"): confirmar.
- Achicar fotos con Pillow (requiere dependency-auditor).
- Login: redirección abierta `siguiente=//...` (cerrar antes de un Tunnel).
<!-- /PUNTO-DE-CONTROL -->
