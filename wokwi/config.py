"""Configuración central del sistema de seguridad."""

# Identidad del dispositivo
DEVICE_ID = "SEG_G8_01"

# Pines de sensores
PIN_PIR = 14
PIN_TRIG = 5
PIN_ECHO = 18

# Pines de actuadores
PIN_LED = 27
PIN_BUZZER = 26

# Parámetros
DISTANCIA_ALERTA = 50         # cm: por debajo de esto se considera intruso
INTERVALO_MUESTREO_MS = 1000  # ms entre lecturas periódicas (Timer)
DEBOUNCE_MS = 250             # ms mínimos entre dos interrupciones del PIR
TIMEOUT_ECO = 30000           # microsegundos máximos de espera del eco

# WiFi (red virtual de Wokwi)
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""
WIFI_TIMEOUT = 15             # segundos máximos esperando conexión

# Hora
INTERVALO_NTP_MS = 60000      # ms entre reintentos de NTP si no sincronizó

# MQTT 
MQTT_BROKER = "broker.emqx.io"
MQTT_PUERTO = 1883
MQTT_REINTENTO_MS = 5000      # ms entre intentos de reconexión al broker
MQTT_CLIENT_PREFIJO = "utp_g8_"   # se le agrega el ID único del chip
TOPIC_BASE = "utp/fisc/ds8/seguridad_g8"
TOPIC_LECTURAS = TOPIC_BASE + "/lecturas"
TOPIC_EVENTOS = TOPIC_BASE + "/eventos"
TOPIC_COMANDOS = TOPIC_BASE + "/comandos"

# Seguridad (el token de comandos está en secretos.py)
ARCHIVO_AUDITORIA = "/security_audit.log"

# ThingSpeak (nube)
THINGSPEAK_URL = "https://api.thingspeak.com/update.json"
INTERVALO_NUBE_MS = 20000     # la cuenta gratis exige mínimo 15 s entre envíos

# ThingSpeak TalkBack (comandos desde la nube)
TALKBACK_URL = "https://api.thingspeak.com/talkbacks"
TALKBACK_ID = "58230"
INTERVALO_TALKBACK_MS = 20000   # cada cuánto se consulta la cola de comandos