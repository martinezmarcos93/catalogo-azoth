-- AZOTH · esquema de la base de datos
-- Un solo usuario (Silvio). Libros, ventas y turnos son las tres entidades CRUD.

CREATE TABLE IF NOT EXISTS usuario (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  nombre TEXT NOT NULL,
  clave_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS configuracion (
  clave TEXT PRIMARY KEY,
  valor TEXT
);

CREATE TABLE IF NOT EXISTS libros (
  id TEXT PRIMARY KEY,
  nro INTEGER NOT NULL,
  titulo TEXT NOT NULL,
  autor TEXT DEFAULT '',
  editorial TEXT DEFAULT '',
  anio INTEGER,
  pais TEXT DEFAULT '',
  tapa TEXT DEFAULT 'Tapa blanda',
  paginas INTEGER,
  tema TEXT NOT NULL,
  tipo TEXT NOT NULL,
  estado TEXT NOT NULL,
  precio INTEGER NOT NULL DEFAULT 0,
  ilustrado INTEGER NOT NULL DEFAULT 0,
  nota TEXT DEFAULT '',
  -- ejemplares = stock que queda en el estante. vendido = 1 cuando llega a 0.
  ejemplares INTEGER NOT NULL DEFAULT 1,
  vendido INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ventas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fecha TEXT NOT NULL,
  libro_id TEXT NOT NULL REFERENCES libros(id),
  medio TEXT NOT NULL,
  entrega TEXT NOT NULL,
  precio INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS turnos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nro INTEGER NOT NULL,
  fecha TEXT NOT NULL,
  hora TEXT NOT NULL,
  cliente TEXT NOT NULL,
  diseno TEXT NOT NULL,
  sesion TEXT DEFAULT '1 de 1',
  total INTEGER NOT NULL DEFAULT 0,
  sena INTEGER NOT NULL DEFAULT 0,
  estado TEXT NOT NULL DEFAULT 'Confirmado'
);

CREATE TABLE IF NOT EXISTS instagram_pendiente (
  libro_id TEXT PRIMARY KEY REFERENCES libros(id)
);
