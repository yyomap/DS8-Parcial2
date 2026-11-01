"""Envío de lecturas a ThingSpeak (dashboard en la nube)."""
import json
import time
import urequests
import config
import secretos

_ultimo_envio = None


def enviar_lectura(movimiento, distancia, alarma, armado):
    """Envía una lectura a ThingSpeak, como máximo una vez cada INTERVALO_NUBE_MS."""
    global _ultimo_envio
    ahora = time.ticks_ms()
    if (_ultimo_envio is not None
            and time.ticks_diff(ahora, _ultimo_envio) < config.INTERVALO_NUBE_MS):
        return
    _ultimo_envio = ahora  # se marca antes de enviar: si falla, no insiste cada segundo

    cuerpo = {
        "api_key": secretos.THINGSPEAK_WRITE_KEY,
        "field1": movimiento,
        "field3": int(alarma),
        "field4": int(armado),
    }
    if distancia is not None:
        cuerpo["field2"] = distancia

    try:
        respuesta = urequests.post(
            config.THINGSPEAK_URL,
            data=json.dumps(cuerpo),
            headers={"Content-Type": "application/json"},
        )
        print("ThingSpeak respondió:", respuesta.text)
        respuesta.close()
    except Exception as err:
        print("ERROR al enviar a ThingSpeak:", err)