"""Sistema de seguridad: sensores, alarma, MQTT y control remoto.

Orientado a eventos: un Timer marca cuándo muestrear, el PIR avisa por
interrupción y el bucle principal solo reacciona, sin bloquearse.
"""
import time
from machine import Timer
import config
import secretos
import sensores
import actuadores
import comunicacion
import auditoria
import tiempo
import nube
import talkback

PAUSA_BUCLE_MS = 10   # pausa corta por vuelta para no saturar la CPU

armado = True
alarma_anterior = False
flag_muestreo = False


def hay_intruso(movimiento, distancia):
    """Regla de alarma: movimiento detectado, u objeto muy cerca."""
    cerca = distancia is not None and distancia < config.DISTANCIA_ALERTA
    return movimiento == 1 or cerca


def procesar_comando(comando):
    """Valida el token y ejecuta el comando (ARMAR / DESARMAR)."""
    global armado

    if comando.get("auth_token") != secretos.TOKEN_COMANDOS:
        auditoria.registrar("MQTT", "ACCESO DENEGADO: token inválido o ausente")
        comunicacion.publicar_evento("COMANDO_RECHAZADO", "token inválido o ausente")
        return

    accion = comando.get("cmd")
    if accion == "ARMAR":
        armado = True
        print("AUTORIZADO: sistema armado")
        comunicacion.publicar_evento("COMANDO_EJECUTADO", "ARMAR")
    elif accion == "DESARMAR":
        armado = False
        actuadores.activar_alarma(0)
        print("AUTORIZADO: sistema desarmado")
        comunicacion.publicar_evento("COMANDO_EJECUTADO", "DESARMAR")
    else:
        auditoria.registrar("MQTT", "Comando desconocido: " + str(accion))
        comunicacion.publicar_evento(
            "COMANDO_RECHAZADO", "comando desconocido: " + str(accion)
        )


def revisar_talkback():
    """Ejecuta el siguiente comando de la nube (ARMAR o DESARMAR) si hay uno."""
    texto = talkback.siguiente_comando()
    if texto in ("ARMAR", "DESARMAR"):
        # La API Key del TalkBack hace de autenticación en este canal
        procesar_comando({"cmd": texto, "auth_token": secretos.TOKEN_COMANDOS})
    elif texto:
        auditoria.registrar("TALKBACK", "Comando desconocido: " + texto)
        comunicacion.publicar_evento("COMANDO_RECHAZADO", "talkback: " + texto)


def timer_callback(t):
    """Callback del Timer: solo levanta la bandera de muestreo."""
    global flag_muestreo
    flag_muestreo = True


def muestrear_y_publicar():
    """Lee los sensores, evalúa la alarma, actúa y publica."""
    global alarma_anterior

    movimiento = sensores.leer_movimiento()
    distancia = sensores.medir_distancia()

    alarma = armado and hay_intruso(movimiento, distancia)
    actuadores.activar_alarma(1 if alarma else 0)

    # Solo se publica evento cuando la alarma cambia de estado
    if alarma != alarma_anterior:
        if alarma:
            motivo = "movimiento" if movimiento == 1 else "distancia"
            comunicacion.publicar_evento("ALARMA_ACTIVADA", motivo)
        else:
            comunicacion.publicar_evento("ALARMA_DESACTIVADA")
        alarma_anterior = alarma

    comunicacion.publicar_lectura(movimiento, distancia, alarma, armado)
    nube.enviar_lectura(movimiento, distancia, alarma, armado)

    print("Armado:", armado, "| Movimiento:", movimiento,
          "| Distancia:", distancia, "cm | Alarma:", alarma)


# Inicialización (antes del bucle)
comunicacion.registrar_manejador(procesar_comando)
wifi_ok = comunicacion.conectar_wifi()
if wifi_ok:
    tiempo.sincronizar_ntp()

if wifi_ok and comunicacion.conectar_mqtt():
    comunicacion.publicar_evento("SISTEMA_INICIADO", "dispositivo en línea")
else:
    print("Modo local: la alarma funciona sin conexión a la nube")

timer_muestreo = Timer(0)
timer_muestreo.init(
    period=config.INTERVALO_MUESTREO_MS,
    mode=Timer.PERIODIC,
    callback=timer_callback,
)

# Bucle principal no bloqueante
while True:
    comunicacion.revisar_comandos()
    revisar_talkback()
    tiempo.reintentar_ntp(config.INTERVALO_NTP_MS)

    evento_pir = sensores.hubo_movimiento()
    if flag_muestreo or evento_pir:
        flag_muestreo = False
        muestrear_y_publicar()

    time.sleep_ms(PAUSA_BUCLE_MS)