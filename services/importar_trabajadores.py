import pandas as pd
from models.models import Trabajador, Empresa

# DEFINIMOS LAS COLUMNAS REQUERIDAS PARA LA IMPORTACION
COLUMNAS_REQUERIDAS = [
    "NOMBRE",
    "NSS",
    "SALARIO",
    "FECHA INGRESO",
    "FECHA BAJA",
    "ENCARGADO",
    "STATUS",
    "EMPRESA"
]

# CREAMOS LA FUNCION PARA LIMPIAR CAMPOS QUE QUEDEN VACIOS
def limpiar_texto(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip()

# CREAMOS LA FUNCION PARA TRANSFORMAR EL VALOR DE STATUS DE TRABAJADOR ACTIVO A TRUE
def convertir_activo(valor):

    valor = limpiar_texto(valor).upper()
    return valor in [
        "SI",
        "SÍ",
        "TRUE",
        "1",
        "ACTIVO",
        "ACTIVA"
    ]

# LEEMOS EL ARCHIVO EXCEL QUE CARGAMOS PARA LA IMPORTACION
def leer_excel(archivo):

    df = pd.read_excel(archivo)
    # Normalizar nombres de columnas
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
    )
    return df

# CREAMOS LA FUNCION PARA VALIDAR QUE LAS COLUMNAS SI ESTEN DENTRO
# EXCEL
def validar_columnas(df):
    columnas_faltantes = [
        columna
        for columna in COLUMNAS_REQUERIDAS
        if columna not in df.columns
    ]

    if columnas_faltantes:
        raise Exception(
            "Faltan las siguientes columnas:\n\n"
            + "\n".join(columnas_faltantes)
        )
    
# PROCESAMOS LA INFORMACION DEL EXCEL Y ENTREGAMOS LOS RESULTADOS DE LA MISMA
# AQUI SERA LA FUNCION PRINCIPAL QUE CARGARA LOS DATOS A BD
def procesar_importacion_trabajadores(df, db):
    
    validar_columnas(df)
    registros_importados = 0
    errores = []
    for indice, fila in df.iterrows():

        try:

            nombre = limpiar_texto(fila["NOMBRE"]).upper()
            nss = limpiar_texto(fila["NSS"])
            salario = float(fila["SALARIO"])

            empresa_id = int(fila["EMPRESA"])

            empresa = Empresa.query.get(
                empresa_id
            )
            activo = convertir_activo(fila["STATUS"])

            fecha_ingreso = pd.to_datetime(
                fila["FECHA INGRESO"]
            ).date()

            fecha_baja = None

            if not pd.isna(
                fila["FECHA BAJA"]
            ):
                fecha_baja = pd.to_datetime(
                    fila["FECHA BAJA"]
                ).date()
            
            encargado = limpiar_texto(
                fila["ENCARGADO"]
            ).upper()

            if not empresa:
                raise Exception(
                    f"No existe la empresa con ID {empresa_id}"
                )

            trabajador = Trabajador(

                nombre_trabajador=nombre,
                nss=nss,
                salario_base=salario,
                fecha_ingreso=fecha_ingreso,
                fecha_baja=fecha_baja,
                encargado=encargado,
                empresa_id=empresa.id,
                activo=activo
            )

            db.session.add(
                trabajador
            )

            registros_importados += 1

        except Exception as e:

            errores.append(
                f"Fila {indice + 2}: {str(e)}"
            )

    db.session.commit()

    return {
        "importados": registros_importados,
        "errores": errores
    }