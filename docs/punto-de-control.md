<!-- PUNTO-DE-CONTROL -->
**Tarea actual:** rama `feat/portada-y-pdf` (sale de `feat/ejemplares-y-turnos`,
ya pusheada; sin commitear todavía): portada (JPG/PNG/WEBP ≤15 MB) y PDF
(≤150 MB) por libro, guardados en `instance/archivos/`, validados por
contenido, servidos solo con login (`/catalogo/<id>/portada|pdf`). La portada
reemplaza al glifo en catálogo/vitrina/panel; el PDF solo se ve en el
catálogo. Reemplazar/quitar/borrar libro limpia el disco. Migración
automática de bases viejas. Service worker a `azoth-estatico-v2`.
28 tests OK + prueba real con curl contra el servidor.

**Próximo paso:** que Marcos revise; commit + push de la rama; decidir
merge de ambas ramas a main. Verlo en el navegador (no se revisó visualmente).

**Bloqueos:** ninguno.

**Archivos en curso:** ninguno a medio terminar.

**Preguntas abiertas:**
- ¿El PDF es solo para Silvio o algún día se vende/entrega al cliente?
- Etiquetas de Instagram ("Librería", "Tatuajes · Solar Estudio", "Silvio"): confirmar.
- Achicar fotos con Pillow (requiere dependency-auditor).
- Login: redirección abierta `siguiente=//...` (cerrar antes de un Tunnel).
<!-- /PUNTO-DE-CONTROL -->
