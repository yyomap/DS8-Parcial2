"""Consulta la cola de comandos de ThingSpeak TalkBack."""
import time
import urequests
import config
import secretos

_ultima_consulta = None


def siguiente_comando():
    """Pide el siguiente comando de la cola, como máximo cada INTERVALO_TALKBACK_MS.
    Devuelve el texto del comando, o None si no hay nada o falla la red."""
    global _ultima_consulta
    ahora = time.ticks_ms()
    if (_ultima_consulta is not None
            and time.ticks_diff(ahora, _ultima_consulta) < config.INTERVALO_TALKBACK_MS):
        return None
    _ultima_consulta = ahora

    url = "{}/{}/commands/execute?api_key={}".format(
        config.TALKBACK_URL, config.TALKBACK_ID, secretos.TALKBACK_API_KEY
    )
    try:
        respuesta = urequests.get(url)
        texto = respuesta.text.strip()
        respuesta.close()
    except Exception as err:
        print("ERROR al consultar TalkBack:", err)
        return None
    return texto or None