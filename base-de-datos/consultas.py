"""Consultas del histórico guardado en seguridad.db."""
import sqlite3
from datetime import datetime, timedelta, timezone

ARCHIVO_DB = "seguridad.db"
PANAMA = timezone(timedelta(hours=-5))


def a_hora_panama(timestamp):
    """Convierte un timestamp Unix (UTC) a texto en hora de Panamá."""
    return datetime.fromtimestamp(timestamp, PANAMA).strftime("%Y-%m-%d %H:%M:%S")


def lecturas_por_rango(bd, desde, hasta):
    """Lecturas entre dos timestamps Unix, solo con hora sincronizada."""
    return bd.execute(
        "SELECT timestamp, movimiento, distancia, alarma, armado "
        "FROM lecturas "
        "WHERE timestamp BETWEEN ? AND ? AND hora_sincronizada = 1 "
        "ORDER BY timestamp",
        (desde, hasta),
    ).fetchall()


def eventos_por_tipo(bd, tipo):
    """Todos los eventos de un tipo, del más viejo al más nuevo."""
    return bd.execute(
        "SELECT timestamp, detalle FROM eventos WHERE tipo = ? ORDER BY timestamp",
        (tipo,),
    ).fetchall()


def contar_alarmas(bd):
    """Cuántas veces se activó la alarma."""
    return bd.execute(
        "SELECT COUNT(*) FROM eventos WHERE tipo = 'ALARMA_ACTIVADA'"
    ).fetchone()[0]


def resumen_eventos(bd):
    """Cantidad de eventos por tipo."""
    return bd.execute(
        "SELECT tipo, COUNT(*) FROM eventos GROUP BY tipo ORDER BY COUNT(*) DESC"
    ).fetchall()


if __name__ == "__main__":
    bd = sqlite3.connect(ARCHIVO_DB)
    ahora = int(datetime.now(timezone.utc).timestamp())

    ultima_hora = lecturas_por_rango(bd, ahora - 3600, ahora)
    print("Lecturas de la última hora:", len(ultima_hora))

    print("\nAlarmas activadas:", contar_alarmas(bd))
    for ts, detalle in eventos_por_tipo(bd, "ALARMA_ACTIVADA"):
        print(" ", a_hora_panama(ts), "| motivo:", detalle)

    print("\nComandos rechazados:")
    for ts, detalle in eventos_por_tipo(bd, "COMANDO_RECHAZADO"):
        print(" ", a_hora_panama(ts), "|", detalle)

    print("\nResumen de eventos por tipo:")
    for tipo, cantidad in resumen_eventos(bd):
        print(" ", tipo, "->", cantidad)
