"""Control de actuadores: LED y buzzer."""
from machine import Pin, PWM
import config

_led = Pin(config.PIN_LED, Pin.OUT)
_buzzer = PWM(Pin(config.PIN_BUZZER))
_buzzer.duty_u16(0)


def activar_alarma(estado):
    """Enciende (1) o apaga (0) el LED y el buzzer a la vez."""
    _led.value(estado)
    if estado:
        _buzzer.freq(2000)
        _buzzer.duty_u16(32768)
    else:
        _buzzer.duty_u16(0)