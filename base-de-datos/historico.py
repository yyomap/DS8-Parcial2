"""Escucha los topics MQTT del sistema de seguridad y guarda todo en SQLite."""
import json
import sqlite3
import paho.mqtt.client as mqtt

BROKER = "broker.emqx.io"
PUERTO = 1883
BASE = "utp/fisc/ds8/seguridad_g8"
ARCHIVO_DB = "seguridad.db"


def preparar_bd():
    """Abre la base y crea las tablas con schema.sql si no existen."""
    conexion = sqlite3.connect(ARCHIVO_DB)
    with open("schema.sql", encoding="utf-8") as archivo:
        conexion.executescript(archivo.read())
    return conexion


def guardar_lectura(bd, d):
    bd.execute(
        "INSERT INTO lecturas (device_id, timestamp, hora_sincronizada, "
        "movimiento, distancia, alarma, armado) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (d["device_id"], d["timestamp"], int(d["hora_sincronizada"]),
         d["movimiento"], d["distancia"], int(d["alarma"]), int(d["armado"])),
    )
    bd.commit()


def guardar_evento(bd, d):
    bd.execute(
        "INSERT INTO eventos (device_id, timestamp, hora_sincronizada, "
        "tipo, detalle) VALUES (?, ?, ?, ?, ?)",
        (d["device_id"], d["timestamp"], int(d["hora_sincronizada"]),
         d["tipo"], d["detalle"]),
    )
    bd.commit()


def al_conectar(cliente, bd, flags, codigo, propiedades):
    """Se suscribe aquí para que también lo haga si la conexión se reinicia."""
    print("Conectado al broker, código:", codigo)
    cliente.subscribe([(BASE + "/lecturas", 0), (BASE + "/eventos", 0)])


def al_recibir(cliente, bd, msg):
    """Decodifica el mensaje y lo guarda en la tabla que corresponde."""
    try:
        datos = json.loads(msg.payload.decode("utf-8"))
        if msg.topic.endswith("/lecturas"):
            guardar_lectura(bd, datos)
        elif msg.topic.endswith("/eventos"):
            guardar_evento(bd, datos)
        print("Guardado:", msg.topic)
    except (ValueError, KeyError) as err:
        print("Mensaje ignorado:", err)


bd = preparar_bd()
cliente = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="utp_g8_pc_historico",
    userdata=bd,
)
cliente.on_connect = al_conectar
cliente.on_message = al_recibir
cliente.connect(BROKER, PUERTO, 60)
cliente.loop_forever()
