"""Manejo de la hora: sincronización NTP y timestamps Unix en UTC."""
import time
import ntptime

# Segundos entre 1970 y 2000 (el reloj de MicroPython en ESP32 parte del 2000)
_OFFSET_2000_A_1970 = 946684800
_sincronizada = False
_ultimo_intento = None


def sincronizar_ntp():
    """Sincroniza el reloj con un servidor NTP. Devuelve True si lo logra."""
    global _sincronizada
    try:
        ntptime.settime()
        _sincronizada = True
        ahora = time.gmtime()
        print("Hora NTP sincronizada (UTC): {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*ahora[:6]))
    except OSError as err:
        _sincronizada = False
        print("FALLO NTP: no se pudo obtener la hora:", err)
    return _sincronizada


def reintentar_ntp(intervalo_ms):
    """Si la hora sigue sin sincronizar, reintenta NTP cada intervalo_ms."""
    global _ultimo_intento
    if _sincronizada:
        return
    ahora = time.ticks_ms()
    if (_ultimo_intento is not None
            and time.ticks_diff(ahora, _ultimo_intento) < intervalo_ms):
        return
    _ultimo_intento = ahora
    sincronizar_ntp()


def hora_sincronizada():
    """Indica si el reloj fue sincronizado con NTP."""
    return _sincronizada


def timestamp_unix():
    """Devuelve los segundos desde 1970 (UTC), corrigiendo la época del puerto."""
    segundos = time.time()
    if time.gmtime(0)[0] == 2000:
        segundos += _OFFSET_2000_A_1970
    return segundos