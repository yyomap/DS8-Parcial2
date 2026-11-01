"""Registro de auditoría: guarda los eventos de seguridad anómalos."""
import config
import tiempo


def registrar(origen, motivo):
    """Escribe un evento rechazado o anómalo en el log y en consola."""
    entrada = "{} | ORIGEN: {} | MOTIVO: {}\n".format(
        tiempo.timestamp_unix(), origen, motivo
    )
    print("AUDITORÍA:", motivo)
    try:
        with open(config.ARCHIVO_AUDITORIA, "a") as archivo:
            archivo.write(entrada)
    except OSError as err:
        print("No se pudo escribir el log:", err)