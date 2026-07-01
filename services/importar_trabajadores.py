import pandas as pd
from models.models import Trabajador, Empresa

# DEFINIMOS LAS COLUMNAS REQUERIDAS PARA LA IMPORTACION
COLUMNAS_REQUERIDAS = [
    "NOMBRE",
    "NSS",
    "SALARIO",
    "CURP",
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
    registros_nuevos = 0
    registros_actualizados = 0
    errores = [] # Manejamos un listado de errores si los encuentra sean visualizados
    advertencias = [] # si vemos un ajuste nos marque una advertencia
    nss_importados = set() #Validamos que no haya NSS repetidos

    for indice, fila in df.iterrows():

        try:

            nombre_original = limpiar_texto(
                fila["NOMBRE"]
            )
            nombre = nombre_original.upper()
            if nombre != nombre_original:
                advertencias.append(
                    f"Fila {indice + 2}: El nombre fue convertido a mayúsculas."
                )

            nss = limpiar_texto(
                fila["NSS"]
            )
            if not nss:
                raise Exception(
                    "El NSS es obligatorio."
                )
            if nss in nss_importados:
                raise Exception(
                    f"El NSS {nss} está repetido en el archivo."
                )
            nss_importados.add(nss)

            curp_original = limpiar_texto(fila["CURP"])
            curp = (
                curp_original.replace(" ", "").upper()
            )
            if curp != "" and len(curp) != 18:
                raise Exception(
                    f"El CURP '{curp}' debe contener 18 caracteres."
                )
            if curp != curp_original:
                advertencias.append(
                    f"Fila {indice + 2}: El CURP fue normalizado."
                )
            
            salario_original = str(fila["SALARIO"])
            salario = float(salario_original.replace(",", "."))

            if salario_original != str(salario):
                advertencias.append(
                    f"Fila {indice + 2}: El formato del salario fue corregido."
                )

            empresa_id = int(fila["EMPRESA"])
            empresa = Empresa.query.get(empresa_id)
            if not empresa:
                raise Exception(
                    f"No existe la empresa con ID {empresa_id}."
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
            
            if fecha_baja:
                if fecha_baja < fecha_ingreso:
                    raise Exception(
                        "La fecha de baja no puede ser menor que la fecha de ingreso."
                    )

            encargado = limpiar_texto(
                fila["ENCARGADO"]
            ).upper()
            
            trabajador = Trabajador.query.filter_by(
                nss=nss
            ).first()

            # Si no existe, lo creamos
            if trabajador is None:
                
                trabajador = Trabajador(

                    nombre_trabajador=nombre,
                    nss=nss,
                    salario_base=salario,
                    curp=curp,
                    fecha_ingreso=fecha_ingreso,
                    fecha_baja=fecha_baja,
                    encargado=encargado,
                    empresa_id=empresa.id,
                    activo=activo
                )

                db.session.add(
                    trabajador
                )

                advertencias.append(
                    f"Fila {indice + 2}: Se creó un nuevo trabajador."
                )

                registros_nuevos += 1

            # Si existe, actualizamos únicamente los campos que cambiaron
            if trabajador.nombre_trabajador != nombre:

                advertencias.append(
                    f"Fila {indice + 2}: Nombre actualizado."
                )
                trabajador.nombre_trabajador = nombre


            if trabajador.curp != curp:

                advertencias.append(
                    f"Fila {indice + 2}: CURP actualizado."
                )
                trabajador.curp = curp


            if trabajador.salario_base != salario:

                advertencias.append(
                    f"Fila {indice + 2}: Salario actualizado."
                )
                trabajador.salario_base = salario


            if trabajador.fecha_ingreso != fecha_ingreso:

                advertencias.append(
                    f"Fila {indice + 2}: Fecha de ingreso actualizada."
                )
                trabajador.fecha_ingreso = fecha_ingreso


            if trabajador.fecha_baja != fecha_baja:

                advertencias.append(
                    f"Fila {indice + 2}: Fecha de baja actualizada."
                )
                trabajador.fecha_baja = fecha_baja


            if trabajador.encargado != encargado:

                advertencias.append(
                    f"Fila {indice + 2}: Encargado actualizado."
                )
                trabajador.encargado = encargado


            if trabajador.empresa_id != empresa.id:

                advertencias.append(
                    f"Fila {indice + 2}: Empresa actualizada."
                )
                trabajador.empresa_id = empresa.id


            if trabajador.activo != activo:

                advertencias.append(
                    f"Fila {indice + 2}: Estatus actualizado."
                )
                trabajador.activo = activo

            if trabajador is None:
                registros_nuevos += 1
            else:
                registros_actualizados += 1

        except Exception as e:
            db.session.rollback()
            errores.append(
                f"Fila {indice + 2}: {str(e)}"
            )

    if registros_nuevos > 0 or registros_actualizados > 0:
        db.session.commit()
        
    return {
        "procesados": len(df),
        "importados": registros_nuevos,
        "actualizados": registros_actualizados,
        "advertencias": advertencias,
        "total_advertencias": len(advertencias),
        "errores": errores,
        "total_errores": len(errores)
    }