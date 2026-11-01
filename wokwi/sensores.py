"""Lectura de sensores: PIR (movimiento, por interrupción) y HC-SR04 (distancia)."""
from machine import Pin, time_pulse_us
import machine
import time
import config

_pir = Pin(config.PIN_PIR, Pin.IN)
_trig = Pin(config.PIN_TRIG, Pin.OUT)
_echo = Pin(config.PIN_ECHO, Pin.IN)

_evento_pendiente = False
_ultimo_evento = 0


def _isr_pir(pin):
    """Interrupción del PIR: marca el evento, filtrando rebotes."""
    global _evento_pendiente, _ultimo_evento
    ahora = time.ticks_ms()
    if time.ticks_diff(ahora, _ultimo_evento) > config.DEBOUNCE_MS:
        _ultimo_evento = ahora
        _evento_pendiente = True


_pir.irq(trigger=Pin.IRQ_RISING, handler=_isr_pir)


def hubo_movimiento():
    """Devuelve True una sola vez por cada evento detectado por el PIR."""
    global _evento_pendiente
    estado = machine.disable_irq()
    pendiente = _evento_pendiente
    _evento_pendiente = False
    machine.enable_irq(estado)
    return pendiente


def leer_movimiento():
    """Devuelve 1 si el PIR está detectando movimiento ahora, 0 si no."""
    return _pir.value()


def medir_distancia():
    """Devuelve la distancia en cm, o None si no hubo eco."""
    _trig.value(0)
    time.sleep_us(2)
    _trig.value(1)
    time.sleep_us(10)
    _trig.value(0)

    duracion = time_pulse_us(_echo, 1, config.TIMEOUT_ECO)
    if duracion < 0:
        return None
    return round(duracion * 0.0343 / 2, 1)