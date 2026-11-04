"""Tests de punta a punta con el cliente de pruebas de Flask.

Uso (desde la raíz del repo):
    python -m unittest discover -s tests -v
"""
import io
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from app import create_app
from app import basedatos as db

RAIZ = Path(__file__).resolve().parent.parent
CLAVE = "abcd"


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.app = create_app({"DATABASE": str(Path(self.tmp) / "t.db"),
                               "ARCHIVOS": str(Path(self.tmp) / "archivos"), "TESTING": True})
        self.c = self.app.test_client()
        self.c.post("/primer-ingreso", data={"clave": CLAVE, "clave_repetida": CLAVE})
        self.c.get("/")  # consume el aviso de "Contraseña creada"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def crear_libro(self, titulo="Kybalion", ejemplares=1, precio=15000):
        self.c.post("/catalogo/crear", data={
            "titulo": titulo, "tema": "Hermetismo", "tipo": "Usado",
            "estado": "Sin roturas, ni escritos", "precio": str(precio),
            "ejemplares": str(ejemplares),
        })
        with self.app.app_context():
            return next(b for b in db.listar_libros() if b["titulo"] == titulo)["id"]

    def libro(self, libro_id):
        with self.app.app_context():
            return db.obtener_libro(libro_id)

    def vender(self, libro_id):
        return self.c.post("/ventas/crear", data={"libro_id": libro_id, "precio": "15000"},
                           follow_redirects=True)

    def cantidad_ventas(self):
        with self.app.app_context():
            return len(db.listar_ventas())


class TestPantallas(BaseTest):
    def test_todas_las_pantallas_cargan(self):
        self.crear_libro()
        for ruta in ["/", "/catalogo", "/vitrina", "/ventas", "/turnos",
                     "/calculadora?costo=1000&margen=30", "/configuracion",
                     "/catalogo/importar", "/catalogo/planilla.csv"]:
            with self.subTest(ruta=ruta):
                self.assertEqual(self.c.get(ruta).status_code, 200)

    def test_sin_sesion_redirige_al_login(self):
        otro = self.app.test_client()
        r = otro.get("/catalogo")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login", r.headers["Location"])


class TestEjemplares(BaseTest):
    def test_libro_con_un_ejemplar_no_se_vende_dos_veces(self):
        lid = self.crear_libro(ejemplares=1)
        self.vender(lid)
        r = self.vender(lid)
        self.assertIn("No quedan ejemplares", r.get_data(as_text=True))
        self.assertEqual(self.cantidad_ventas(), 1)
        self.assertEqual(self.libro(lid)["vendido"], 1)

    def test_con_stock_se_vende_varias_veces_hasta_agotar(self):
        lid = self.crear_libro(ejemplares=3)
        self.vender(lid)
        libro = self.libro(lid)
        self.assertEqual((libro["ejemplares"], libro["vendido"]), (2, 0))
        with self.app.app_context():
            self.assertEqual(db.listar_instagram_pendiente(), [])  # sigue en venta
        self.vender(lid)
        self.vender(lid)
        libro = self.libro(lid)
        self.assertEqual((libro["ejemplares"], libro["vendido"]), (0, 1))
        with self.app.app_context():
            self.assertEqual([b["id"] for b in db.listar_instagram_pendiente()], [lid])
        self.vender(lid)
        self.assertEqual(self.cantidad_ventas(), 3)

    def test_anular_venta_devuelve_el_ejemplar(self):
        lid = self.crear_libro(ejemplares=1)
        self.vender(lid)
        with self.app.app_context():
            venta_id = db.listar_ventas()[0]["id"]
        self.c.post(f"/ventas/{venta_id}/eliminar")
        libro = self.libro(lid)
        self.assertEqual((libro["ejemplares"], libro["vendido"]), (1, 0))
        with self.app.app_context():
            self.assertEqual(db.listar_instagram_pendiente(), [])

    def test_reponer_stock_al_editar_vuelve_a_la_vitrina(self):
        lid = self.crear_libro(ejemplares=1)
        self.vender(lid)
        self.c.post(f"/catalogo/{lid}/actualizar", data={
            "titulo": "Kybalion", "tema": "Hermetismo", "tipo": "Usado",
            "estado": "Sin roturas, ni escritos", "precio": "15000", "ejemplares": "2",
        })
        libro = self.libro(lid)
        self.assertEqual((libro["ejemplares"], libro["vendido"]), (2, 0))
        self.assertIn("Kybalion", self.c.get("/vitrina").get_data(as_text=True))

    def test_valor_del_estante_cuenta_ejemplares(self):
        self.crear_libro(ejemplares=3, precio=10000)
        self.assertIn("$30.000", self.c.get("/").get_data(as_text=True))


class TestBorrarLibros(BaseTest):
    def test_libro_vendido_no_se_borra(self):
        lid = self.crear_libro()
        self.vender(lid)
        r = self.c.post(f"/catalogo/{lid}/eliminar", follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        self.assertIn("tiene ventas registradas", r.get_data(as_text=True))
        self.assertIsNotNone(self.libro(lid))

    def test_libro_sin_ventas_se_borra(self):
        lid = self.crear_libro()
        self.c.post(f"/catalogo/{lid}/eliminar")
        self.assertIsNone(self.libro(lid))

    def test_boton_eliminar_oculto_si_tiene_ventas(self):
        vendido = self.crear_libro("Vendido")
        libre = self.crear_libro("Libre")
        self.vender(vendido)
        html = self.c.get("/catalogo").get_data(as_text=True)
        self.assertNotIn(f"/catalogo/{vendido}/eliminar", html)
        self.assertIn(f"/catalogo/{libre}/eliminar", html)


class TestTurnos(BaseTest):
    def datos(self, **cambios):
        d = {"fecha": "2026-11-05", "hora": "15:00", "cliente": "Ana",
             "diseno": "Rosa", "total": "50000", "sena": "10000"}
        d.update(cambios)
        return d

    def test_fecha_invalida_se_rechaza_y_la_pantalla_sigue_andando(self):
        r = self.c.post("/turnos/crear", data=self.datos(fecha="no-es-fecha"), follow_redirects=True)
        self.assertIn("fecha del turno no es válida", r.get_data(as_text=True))
        self.assertEqual(self.c.get("/turnos").status_code, 200)
        with self.app.app_context():
            self.assertEqual(db.listar_turnos(), [])

    def test_hora_invalida_se_rechaza(self):
        self.c.post("/turnos/crear", data=self.datos(hora="25:99"))
        with self.app.app_context():
            self.assertEqual(db.listar_turnos(), [])

    def test_editar_turno_tambien_valida(self):
        self.c.post("/turnos/crear", data=self.datos())
        with self.app.app_context():
            tid = db.listar_turnos()[0]["id"]
        self.c.post(f"/turnos/{tid}/actualizar", data=self.datos(fecha="2026-13-45"))
        with self.app.app_context():
            self.assertEqual(db.obtener_turno(tid)["fecha"], "2026-11-05")

    def test_turno_viejo_con_fecha_rota_no_rompe_la_pantalla(self):
        with self.app.app_context():
            db.crear_turno({"fecha": "basura", "hora": "15:00", "cliente": "X", "diseno": "Y",
                            "sesion": "1 de 1", "total": 0, "sena": 0, "estado": "Confirmado"})
        self.assertEqual(self.c.get("/turnos").status_code, 200)


class TestConfiguracion(BaseTest):
    def test_datos_reales_por_defecto(self):
        with self.app.app_context():
            sitio = db.obtener_config_sitio()
        self.assertEqual(sitio["whatsapp_numero"], "5491137869154")
        self.assertEqual([c["usuario"] for c in sitio["instagram_cuentas"]],
                         ["azothlibreria", "solarestudioba", "silviocaveira"])

    def test_si_borra_todas_las_cuentas_no_vuelven_solas(self):
        for cuenta_id in (1, 2, 3):
            self.c.post(f"/configuracion/instagram/{cuenta_id}/eliminar")
        with self.app.app_context():
            self.assertEqual(db.listar_instagram_cuentas(), [])


class TestImportar(BaseTest):
    def subir(self, filas):
        wb = load_workbook(RAIZ / "app/static/plantillas/azoth-catalogo-plantilla.xlsx")
        hoja = wb["Catálogo"]
        hoja.delete_rows(3, 2)
        for i, fila in enumerate(filas, start=3):
            for j, valor in enumerate(fila, start=1):
                hoja.cell(row=i, column=j, value=valor)
        buf = io.BytesIO(); wb.save(buf); buf.seek(0)
        self.c.post("/catalogo/importar", data={"archivo": (buf, "cat.xlsx")},
                    content_type="multipart/form-data")
        with self.app.app_context():
            return {b["titulo"]: b for b in db.listar_libros()}

    def test_importa_ejemplares_y_toma_1_si_falta(self):
        base = ["", "", 2000, "Argentina", "Tapa blanda", 100, "Tarot", "Usado",
                "Sin roturas, ni escritos", 9000, "No", ""]
        libros = self.subir([["Con tres"] + base + [3], ["Sin columna"] + base])
        self.assertEqual(libros["Con tres"]["ejemplares"], 3)
        self.assertEqual(libros["Sin columna"]["ejemplares"], 1)


JPG = b"\xff\xd8\xff\xe0" + b"\x00" * 200
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 200
PDF = b"%PDF-1.4\n" + b"x" * 500 + b"\n%%EOF"
CAMPOS = {"titulo": "Kybalion", "tema": "Hermetismo", "tipo": "Usado",
          "estado": "Sin roturas, ni escritos", "precio": "15000", "ejemplares": "1"}


class TestArchivos(BaseTest):
    def enviar(self, ruta, **archivos_y_campos):
        datos = dict(CAMPOS)
        for clave, valor in archivos_y_campos.items():
            datos[clave] = (io.BytesIO(valor[1]), valor[0]) if isinstance(valor, tuple) else valor
        return self.c.post(ruta, data=datos, content_type="multipart/form-data",
                           follow_redirects=True)

    def carpeta(self):
        return sorted(p.name for p in (Path(self.tmp) / "archivos").glob("*"))

    def un_libro(self):
        with self.app.app_context():
            return db.listar_libros()[0]

    def test_crear_con_portada_y_pdf(self):
        self.enviar("/catalogo/crear", portada=("tapa.jpg", JPG), pdf=("libro.pdf", PDF))
        b = self.un_libro()
        self.assertTrue(b["portada"].endswith(".jpg"))
        self.assertTrue(b["pdf"].endswith(".pdf"))
        r = self.c.get(f"/catalogo/{b['id']}/portada")
        self.assertEqual((r.status_code, r.mimetype, r.data), (200, "image/jpeg", JPG))
        r.close()
        r = self.c.get(f"/catalogo/{b['id']}/pdf")
        self.assertEqual((r.status_code, r.mimetype, r.data), (200, "application/pdf", PDF))
        r.close()
        r = self.c.get(f"/catalogo/{b['id']}/pdf?descargar=1")
        self.assertIn("attachment", r.headers["Content-Disposition"])
        r.close()
        html = self.c.get("/vitrina").get_data(as_text=True)
        self.assertIn(f"/catalogo/{b['id']}/portada", html)
        self.assertNotIn(f"/catalogo/{b['id']}/pdf", html)  # el PDF no se muestra al cliente

    def test_el_tipo_se_reconoce_por_el_contenido(self):
        r = self.enviar("/catalogo/crear", portada=("virus.jpg", b"MZ\x90\x00" + b"\x00" * 100))
        self.assertIn("tiene que ser una foto", r.get_data(as_text=True))
        with self.app.app_context():
            self.assertEqual(db.listar_libros(), [])  # no se cargó el libro a medias
        r = self.enviar("/catalogo/crear", pdf=("falso.pdf", JPG))
        self.assertIn("no es un PDF", r.get_data(as_text=True))
        self.assertEqual(self.carpeta(), [])

    def test_png_queda_como_png_aunque_se_llame_jpg(self):
        self.enviar("/catalogo/crear", portada=("foto.jpg", PNG))
        self.assertTrue(self.un_libro()["portada"].endswith(".png"))

    def test_reemplazar_borra_el_archivo_viejo(self):
        self.enviar("/catalogo/crear", portada=("a.jpg", JPG))
        b = self.un_libro()
        self.enviar(f"/catalogo/{b['id']}/actualizar", portada=("b.png", PNG))
        nuevo = self.un_libro()["portada"]
        self.assertNotEqual(nuevo, b["portada"])
        self.assertEqual(self.carpeta(), [nuevo])

    def test_editar_sin_archivo_no_toca_lo_cargado(self):
        self.enviar("/catalogo/crear", portada=("a.jpg", JPG), pdf=("l.pdf", PDF))
        b = self.un_libro()
        self.enviar(f"/catalogo/{b['id']}/actualizar", precio="20000")
        despues = self.un_libro()
        self.assertEqual((despues["portada"], despues["pdf"]), (b["portada"], b["pdf"]))
        self.assertEqual(despues["precio"], 20000)

    def test_quitar_portada_y_pdf(self):
        self.enviar("/catalogo/crear", portada=("a.jpg", JPG), pdf=("l.pdf", PDF))
        b = self.un_libro()
        self.enviar(f"/catalogo/{b['id']}/actualizar", quitar_portada="on", quitar_pdf="on")
        despues = self.un_libro()
        self.assertEqual((despues["portada"], despues["pdf"]), ("", ""))
        self.assertEqual(self.carpeta(), [])
        self.assertEqual(self.c.get(f"/catalogo/{b['id']}/portada").status_code, 404)

    def test_borrar_libro_borra_sus_archivos(self):
        self.enviar("/catalogo/crear", portada=("a.jpg", JPG), pdf=("l.pdf", PDF))
        self.c.post(f"/catalogo/{self.un_libro()['id']}/eliminar")
        self.assertEqual(self.carpeta(), [])

    def test_archivos_protegidos_por_login(self):
        self.enviar("/catalogo/crear", portada=("a.jpg", JPG), pdf=("l.pdf", PDF))
        lid = self.un_libro()["id"]
        anonimo = self.app.test_client()
        for tipo in ("portada", "pdf"):
            r = anonimo.get(f"/catalogo/{lid}/{tipo}")
            self.assertEqual(r.status_code, 302)
            self.assertIn("/login", r.headers["Location"])

    def test_archivo_demasiado_grande(self):
        self.app.config["MAX_CONTENT_LENGTH"] = 1000
        r = self.enviar("/catalogo/crear", pdf=("l.pdf", PDF + b"x" * 2000))
        self.assertIn("demasiado grande", r.get_data(as_text=True))

    def test_pantallas_con_portada_cargan(self):
        self.enviar("/catalogo/crear", portada=("a.jpg", JPG), pdf=("l.pdf", PDF))
        for ruta in ("/", "/catalogo", "/vitrina", "/ventas"):
            with self.subTest(ruta=ruta):
                self.assertEqual(self.c.get(ruta).status_code, 200)


class TestMigracion(unittest.TestCase):
    def test_base_vieja_sin_columna_ejemplares(self):
        tmp = tempfile.mkdtemp()
        ruta = Path(tmp) / "vieja.db"
        con = sqlite3.connect(ruta)
        esquema_viejo = (RAIZ / "app/schema.sql").read_text(encoding="utf-8")
        esquema_viejo = esquema_viejo.replace("  ejemplares INTEGER NOT NULL DEFAULT 1,\n", "")
        esquema_viejo = esquema_viejo.replace("  portada TEXT NOT NULL DEFAULT '',\n", "")
        esquema_viejo = esquema_viejo.replace("  pdf TEXT NOT NULL DEFAULT '',\n", "")
        self.assertNotIn("portada TEXT", esquema_viejo)
        con.executescript(esquema_viejo)
        con.execute("INSERT INTO libros (id, nro, titulo, tema, tipo, estado, vendido) "
                    "VALUES ('a', 1, 'Vendido', 'Tarot', 'Usado', 'x', 1), "
                    "('b', 2, 'Disponible', 'Tarot', 'Usado', 'x', 0)")
        con.commit(); con.close()
        app = create_app({"DATABASE": str(ruta), "TESTING": True})
        with app.app_context():
            self.assertEqual(db.obtener_libro("a")["ejemplares"], 0)
            self.assertEqual(db.obtener_libro("b")["ejemplares"], 1)
            self.assertEqual(db.obtener_libro("b")["portada"], "")
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
