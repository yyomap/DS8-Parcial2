CREATE TABLE IF NOT EXISTS lecturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    hora_sincronizada INTEGER NOT NULL,
    movimiento INTEGER,
    distancia REAL,
    alarma INTEGER,
    armado INTEGER
);

CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    hora_sincronizada INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    detalle TEXT
);

CREATE INDEX IF NOT EXISTS idx_lecturas_ts ON lecturas(timestamp);
CREATE INDEX IF NOT EXISTS idx_eventos_tipo ON eventos(tipo);
