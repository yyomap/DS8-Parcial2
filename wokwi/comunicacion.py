"""Comunicación: conexión WiFi y cliente MQTT (publicar y recibir)."""
import network
import time
import json
import ubinascii
import machine
from umqtt.simple import MQTTClient
import config
import auditoria
import tiempo
import random

_cliente = None
_manejador = None
_ultimo_intento = 0


def _generar_client_id():
    """CLIENT_ID único: ID del chip más un sufijo aleatorio por arranque."""
    id_chip = ubinascii.hexlify(machine.unique_id()).decode()
    sufijo = "{:04x}".format(random.getrandbits(16))
    return config.MQTT_CLIENT_PREFIJO + id_chip + "_" + sufijo


def _perder_conexion(err):
    """Descarta el cliente roto para que se pueda volver a conectar."""
    global _cliente
    print("Conexión MQTT perdida:", err)
    try:
        _cliente.sock.close()
    except Exception:
        pass
    _cliente = None


def _reintentar():
    """Intenta reconectar, pero no más de una vez cada MQTT_REINTENTO_MS."""
    global _ultimo_intento
    ahora = time.ticks_ms()
    if time.ticks_diff(ahora, _ultimo_intento) < config.MQTT_REINTENTO_MS:
        return
    _ultimo_intento = ahora
    print("Reintentando conexión MQTT...")
    if conectar_mqtt():
        publicar_evento("MQTT_RECONECTADO", "conexión recuperada")


def _publicar(topic, mensaje):
    """Publica un mensaje; si no hay conexión o falla, no detiene el programa."""
    if _cliente is None:
        return
    try:
        _cliente.publish(topic, mensaje.encode("utf-8"))
    except OSError as err:
        _perder_conexion("al publicar: " + str(err))


def _al_recibir(topic, mensaje):
    """Callback: decodifica el mensaje, lo parsea como JSON y lo entrega."""
    try:
        texto = mensaje.decode("utf-8")
        comando = json.loads(texto)
        if not isinstance(comando, dict):
            raise ValueError("el JSON no es un objeto")
    except ValueError as err:
        auditoria.registrar(
            topic.decode(), "Mensaje corrupto o JSON no válido: " + str(err)
        )
        publicar_evento("COMANDO_RECHAZADO", "mensaje corrupto o JSON no válido")
        return

    if _manejador:
        _manejador(comando)


def registrar_manejador(funcion):
    """Registra la función que procesará cada comando recibido."""
    global _manejador
    _manejador = funcion


def conectar_wifi():
    """Conecta al WiFi con tiempo límite. Devuelve True si lo logra."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        return True

    print("Conectando a SSID:", config.WIFI_SSID)
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

    inicio = time.time()
    while not wlan.isconnected():
        if time.time() - inicio > config.WIFI_TIMEOUT:
            print("ERROR: timeout al conectar a WiFi")
            return False
        time.sleep(0.5)

    print("WiFi conectado:", wlan.ifconfig()[0])
    return True


def conectar_mqtt():
    """Conecta al broker y se suscribe a comandos. Devuelve True si lo logra."""
    global _cliente
    try:
        client_id = _generar_client_id()
        _cliente = MQTTClient(
            client_id, config.MQTT_BROKER, port=config.MQTT_PUERTO
        )
        _cliente.set_callback(_al_recibir)
        _cliente.connect()
        _cliente.subscribe(config.TOPIC_COMANDOS)
        print("MQTT conectado a", config.MQTT_BROKER, "como", client_id)
        return True
    except Exception as err:
        print("ERROR de conexión MQTT:", err)
        _cliente = None
        return False


def revisar_comandos():
    """Revisa (sin bloquear) si llegaron comandos nuevos; reconecta si hace falta."""
    if _cliente is None:
        _reintentar()
        return
    try:
        _cliente.check_msg()
    except OSError as err:
        _perder_conexion("al revisar: " + str(err))


def publicar_lectura(movimiento, distancia, alarma, armado):
    """Publica una lectura de sensores como JSON, con dispositivo y hora."""
    _publicar(config.TOPIC_LECTURAS, json.dumps({
        "device_id": config.DEVICE_ID,
        "timestamp": tiempo.timestamp_unix(),
        "hora_sincronizada": tiempo.hora_sincronizada(),
        "movimiento": movimiento,
        "distancia": distancia,
        "alarma": alarma,
        "armado": armado,
    }))


def publicar_evento(tipo, detalle=""):
    """Publica un evento puntual (alarma, comando ejecutado o rechazado)."""
    _publicar(config.TOPIC_EVENTOS, json.dumps({
        "device_id": config.DEVICE_ID,
        "timestamp": tiempo.timestamp_unix(),
        "hora_sincronizada": tiempo.hora_sincronizada(),
        "tipo": tipo,
        "detalle": detalle,
    }))