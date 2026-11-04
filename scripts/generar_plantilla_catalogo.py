"""Genera app/static/plantillas/azoth-catalogo-plantilla.xlsx.

Se corre a mano cuando cambian las columnas del catálogo (TEMAS, TIPOS,
ESTADOS, TAPAS en app/utilidades.py). No se ejecuta en cada arranque de
la app: el archivo generado queda versionado como archivo estático.

Uso:
    python scripts/generar_plantilla_catalogo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

from app.utilidades import ESTADOS, TAPAS, TEMAS, TIPOS

COLUMNAS = [
    ("Título", 32), ("Autor", 22), ("Editorial", 22), ("Año", 8),
    ("País", 14), ("Tapa", 20), ("Páginas", 10), ("Tema", 16),
    ("Tipo", 18), ("Estado", 34), ("Precio", 12), ("Ilustrado", 11),
    ("Detalle del ejemplar", 36), ("Ejemplares", 12),
]
SI_NO = ["Sí", "No"]

EJEMPLOS = [
    ["(EJEMPLO) El libro de los esplendores", "Éliphas Lévi", "Editorial Kier",
     1961, "Argentina", "Tapa blanda", 220, "Cábala", "Descatalogado",
     ESTADOS[2], 70000, "No", "1ra edición — borrar esta fila antes de importar", 2],
    ["(EJEMPLO) Azoth", "Silvio", "Obra propia", 2026, "Argentina",
     "Tapa blanda", "", "Obra original", "Obra original", "Original firmado",
     0, "Sí", "Tinta y pluma sobre papel de 180 g — borrar esta fila antes de importar", 1],
]

FILAS_CON_VALIDACION = 400  # alcanza y sobra para cargar el catálogo entero

wb = Workbook()
hoja = wb.active
hoja.title = "Catálogo"

FUENTE = "Arial"
hoja.sheet_view.showGridLines = False

# --- Banner de instrucciones ---
hoja.merge_cells("A1:N1")
banner = hoja["A1"]
banner.value = (
    "Completá una fila por libro. Las columnas marcadas con ▾ tienen una lista para elegir: "
    "así no se puede escribir un tema o tipo que el sistema no reconozca. "
    "Ejemplares: cuántas copias hay de ese libro (si se deja vacío, cuenta 1). "
    "Borrá las 2 filas de ejemplo (3 y 4) antes de guardar y subir el archivo."
)
banner.font = Font(name=FUENTE, size=10, italic=True, color="672E37")
banner.fill = PatternFill("solid", start_color="FBEAEC", end_color="FBEAEC")
banner.alignment = Alignment(wrap_text=True, vertical="center")
hoja.row_dimensions[1].height = 34

# --- Encabezado ---
FILA_ENCABEZADO = 2
for col_idx, (nombre, ancho) in enumerate(COLUMNAS, start=1):
    celda = hoja.cell(row=FILA_ENCABEZADO, column=col_idx, value=nombre)
    celda.font = Font(name=FUENTE, size=11, bold=True, color="FFFFFF")
    celda.fill = PatternFill("solid", start_color="202226", end_color="202226")
    celda.alignment = Alignment(horizontal="center", vertical="center")
    hoja.column_dimensions[celda.column_letter].width = ancho
hoja.freeze_panes = "A3"

# --- Filas de ejemplo ---
for fila_offset, ejemplo in enumerate(EJEMPLOS):
    fila = FILA_ENCABEZADO + 1 + fila_offset
    for col_idx, valor in enumerate(ejemplo, start=1):
        celda = hoja.cell(row=fila, column=col_idx, value=valor)
        celda.font = Font(name=FUENTE, size=10, italic=True, color="8A8983")

# --- Fuente de las listas desplegables, en una hoja aparte ---
listas = wb.create_sheet("Listas")
listas.sheet_state = "hidden"
for col_idx, (titulo, valores) in enumerate(
    [("Tapas", TAPAS), ("Temas", TEMAS), ("Tipos", TIPOS), ("Estados", ESTADOS), ("SiNo", SI_NO)],
    start=1,
):
    letra = listas.cell(row=1, column=col_idx, value=titulo).column_letter
    for i, valor in enumerate(valores, start=2):
        listas.cell(row=i, column=col_idx, value=valor)

def _rango(col_letra, cantidad):
    return f"Listas!${col_letra}$2:${col_letra}${cantidad + 1}"

VALIDACIONES = {
    "F": _rango("A", len(TAPAS)),    # Tapa
    "H": _rango("B", len(TEMAS)),    # Tema
    "I": _rango("C", len(TIPOS)),    # Tipo
    "J": _rango("D", len(ESTADOS)),  # Estado
    "L": _rango("E", len(SI_NO)),    # Ilustrado
}
primera_fila_datos = FILA_ENCABEZADO + 1
ultima_fila_datos = FILA_ENCABEZADO + FILAS_CON_VALIDACION
for col_letra, formula in VALIDACIONES.items():
    dv = DataValidation(type="list", formula1=f"={formula}", allow_blank=True, showDropDown=False)
    dv.error = "Elegí un valor de la lista."
    dv.errorTitle = "Valor no válido"
    hoja.add_data_validation(dv)
    dv.add(f"{col_letra}{primera_fila_datos}:{col_letra}{ultima_fila_datos}")

# Formato de columnas numéricas
for fila in range(primera_fila_datos, ultima_fila_datos + 1):
    hoja.cell(row=fila, column=4).number_format = "0"   # Año
    hoja.cell(row=fila, column=7).number_format = "0"   # Páginas
    hoja.cell(row=fila, column=11).number_format = "#,##0"  # Precio
    hoja.cell(row=fila, column=14).number_format = "0"   # Ejemplares

destino = Path(__file__).resolve().parent.parent / "app" / "static" / "plantillas" / "azoth-catalogo-plantilla.xlsx"
destino.parent.mkdir(parents=True, exist_ok=True)
wb.save(destino)
print(f"Guardado: {destino}")
