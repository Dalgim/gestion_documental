import re
import pandas as pd
from models.models import db, Empresa

#Aqui definimos los campos que vamos a requerir dentro del excel para importar datos
COLUMNAS_REQUERIDAS = [

    "NOMBRE",
    "RFC",
    "REPRESENTANTE",
    "DOMICILIO",
    "CORREO",
    "TELEFONO",
    "NIVEL",
    "REGIMEN FISCAL",
    "ACTIVO"

]

# Niveles validos para validacion a la hora de importar datos y haga la revisión
NIVELES_VALIDOS = [
    "1",
    "2",
    "3"
]

# Funcion para limpiar los campos que vengan vacios del excel a la hora de la importación
def limpiar_texto(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip()


# Funcion para validar que la estructura del correo es la adecuada y no haya
# confusiones
def correo_valido(correo):
    # Definimos el patron para determinar la estructura del correo usando expresiones regulares
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(
        patron,
        correo
    ) is not None

# Funcion para convertir el valor del campo ACTIVO en la tabla
def convertir_activo(valor):
    valor = str(valor).strip().upper()
    return valor in [
        "SI",
        "SÍ",
        "TRUE",
        "1",
        "ACTIVA",
        "ACTIVO"
    ]


#vamos a leer el excel y definir que los campos son los correctos
# en caso de tener un error, procedemos a indicar que nos falta columnas
def leer_excel(ruta_archivo):

    df = pd.read_excel(ruta_archivo)

    # Convertir nombres de columnas a mayúsculas
    df.columns = [
        c.upper().strip()
        for c in df.columns
    ]

    columnas_faltantes = []

    for columna in COLUMNAS_REQUERIDAS:
        if columna not in df.columns:
            columnas_faltantes.append(
                columna
            )

    if columnas_faltantes:
        raise Exception(
            "Faltan las columnas: "
            + ", ".join(columnas_faltantes)
        )

    return df

# Creamos el servicio para importar listado a las bases de datos
def procesar_importacion_empresas(df, db):

    importadas = 0
    duplicadas = 0
    errores = []

    for indice, fila in df.iterrows():
        try:
            # Validamos que no haya RFC duplicados
            rfc = str(fila["RFC"]).strip().upper()

            # Si RFC es menor al tamaño entonces es invalido el valor
            if len(rfc) < 12:
                raise Exception(
                    "RFC inválido."
                )
            
            # Validamos el correo
            #correo = str(fila["CORREO"]).strip()
            correo = limpiar_texto(
                fila["CORREO"]
            )

            print(fila["CORREO"])
            print(type(fila["CORREO"]))

            # Mandamos a llamar a la funcion correo_valido
            if correo != "" and not correo_valido(correo):
                raise Exception(
                    "Correo electrónico inválido."
                )
            
            # Validamos el nivel de la empresa
            nivel = str(fila["NIVEL"]).strip()

            if nivel not in NIVELES_VALIDOS:
                raise Exception(
                    "Nivel inválido."
                )

            existe = Empresa.query.filter_by(rfc=rfc).first()

            if existe:
                duplicadas += 1
                continue
            
            # Validamos el nombre de la empresa
            nombre = str(fila["NOMBRE"]).strip().upper()

            if not nombre:
                raise Exception(
                    "El nombre es obligatorio."
                )

            empresa = Empresa(

                nombre=str(fila["NOMBRE"]).strip().upper(),
                rfc=rfc,
                representante=str(fila["REPRESENTANTE"]).strip().upper(),
                domicilio=str(fila["DOMICILIO"]).strip().upper(),
                correo=str(fila["CORREO"]).strip(),
                telefono = limpiar_texto(fila["TELEFONO"]),
                nivel=str(fila["NIVEL"]).strip(),
                activo = convertir_activo(fila["ACTIVO"])
            )

            # Guardamos los datos en la base de datos
            db.session.add(empresa)
            importadas += 1

        except Exception as e:
            errores.append(
                f"Fila {indice+2}: {str(e)}"
            )
    db.session.commit()

    return {
        "importadas": importadas,
        "duplicadas": duplicadas,
        "errores": errores
    }