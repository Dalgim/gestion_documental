from docxtpl import DocxTemplate
from datetime import datetime
import os

# Función para convertir la fecha de inicio en texto
def fecha_letra(fecha):

    meses = {

        1: "ENERO",
        2: "FEBRERO",
        3: "MARZO",
        4: "ABRIL",
        5: "MAYO",
        6: "JUNIO",
        7: "JULIO",
        8: "AGOSTO",
        9: "SEPTIEMBRE",
        10: "OCTUBRE",
        11: "NOVIEMBRE",
        12: "DICIEMBRE"

    }

    if isinstance(fecha, str):

        fecha = datetime.strptime(
            fecha,
            "%Y-%m-%d"
        )

    return (
        f"{fecha.day:02d}"
        f" de "
        f"{meses[fecha.month]}"
        f" de "
        f"{fecha.year}"
    )

def generar_contrato(contexto):

    #ruta_plantilla = os.path.join('plantillas',plantilla.archivo)

    doc = DocxTemplate(
        #"documentos/plantillas/plantilla_cpse_BAIRES.docx"
        "documentos/plantillas/plantilla_cpse_IDINEE.docx"
        #ruta_plantilla
    )

    fecha = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    print(contexto["trabajadores"])

    doc.render(contexto)

    ruta = (
        "documentos/contratos/"
        #f"Contrato_{contexto['CLIENTE']}.docx"
        f"Contrato_{contexto['CLIENTE']}_{fecha}.docx"
    )

    doc.save(ruta)

    return ruta


def actualizar_contrato(
    contexto
):

    fecha = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    nombre_archivo = (
        f"Contrato_{contexto['CLIENTE']}_{fecha}.docx"
    )

    ruta = os.path.join(
        "documentos",
        "contratos",
        nombre_archivo
    )

    return ruta