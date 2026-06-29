from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

"""
Aqui creamos todo el componente de la base de datos, cada clase es una tabla
de la base de datos, si deseas añadir datos a la base de datos solo elimina el archivo
y vuelve a ejecutar app.py en el entorno virtual.

usaremos estructura para las tablas de la siguiente forma:

Tablas dim para catalogos
tablas fact para tablas de hechos (donde se guardaran los contratos)

"""

# Tabla de usuarios para manejar un sistema de login
class Users(UserMixin, db.Model):


    __tablename__ = 'dim_usuarios'

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(200))

    fecha_nacimiento = db.Date

    nombre_usuario = db.Column(db.String(200))

    contraseña = db.Column(db.String(200))

    tipo_usuario = db.Column(db.String(200), default="LEGAL")

    activo = db.Column(db.Boolean, default=True)


# Tabla catalogo de clientes
class Cliente(db.Model):
    
    # Agregammos el nombre que tendra la tabla
    __tablename__ = 'dim_clientes'

    id = db.Column(db.Integer, primary_key=True)

    nombre_cliente = db.Column(db.String(200))

    rfc = db.Column(db.String(20))

    representante = db.Column(db.String(200))

    dom_fiscal = db.Column(db.String(400))

    correo = db.Column(db.String(200))

    nomenclatura = db.Column(db.String(10))


# Tabla para catalogo de empresas prestadoras de servicio
class Empresa(db.Model):

    __tablename__ = "dim_empresas"

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(200), nullable=False, unique=True)

    rfc = db.Column(db.String(13))

    representante = db.Column(db.String(200))

    domicilio = db.Column(db.String(300))

    correo = db.Column(db.String(150))

    telefono = db.Column(db.String(20))

    proyectos = db.relationship(
        "Proyecto",
        backref="empresa",
        lazy=True

    )

    trabajadores = db.relationship(
        "Trabajador",
        backref="empresa",
        lazy=True
    )

    def __repr__(self):
        return self.nombre


# tabla catalogos de servicios especializados
class Proyecto(db.Model):

    __tablename__ = 'dim_servicios'

    id = db.Column(db.Integer, primary_key=True)

    nombre_proyecto = db.Column(db.String(200))

    folio_repse = db.Column(db.String(200))

    act_repse = db.Column(db.String(250))

    tipo_servicio = db.Column(db.String(100))

    empresa_id = db.Column(

        db.Integer,
        db.ForeignKey(
            "dim_empresas.id"
        ),
        nullable=False

    )



# tabla catalogo de trabajadores
class Trabajador(db.Model):

    __tablename__ = 'dim_trabajadores'

    id = db.Column(db.Integer, primary_key=True)

    nombre_trabajador =  db.Column(db.String(200))

    curp = db.Column(db.String(200))

    rfc = db.Column(db.String(200))

    nss = db.Column(db.String(200))

    salario_base = db.Column(db.Float)

    actividades = db.Column(db.String(400))

    puesto = db.Column(db.String(300))

    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "dim_empresas.id"
        ),
        nullable=False
    )


# Tabla donde se guardara los contratos
class Contrato(db.Model):

    __tablename__ = 'fact_contratos'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey('dim_clientes.id'),
        nullable=False
    )

    proyecto_id = db.Column(
        db.Integer,
        db.ForeignKey('dim_servicios.id'),
        nullable=False
    )

    nom_empresa = db.Column(
        db.Text
    )

    nom_cliente = db.Column(
        db.Text
    )

    '''tipo_documento = db.Column(
        db.String(100),
        nullable=False
    )'''

    monto = db.Column(db.Float)

    forma_pago = db.Column(
        db.Text
    )

    fecha_inicio = db.Column(
        db.Date
    )

    fecha_fin = db.Column(
        db.Date
    )

    vigencia = db.Column(
        db.String(50)
    )

    archivo_generado = db.Column(
        db.String(500)
    )

    fecha_generacion = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    #contexto_json = db.Column(
    #    db.Text
    #)

# Tabla para guardar las plantillas de contratos
class PlantillaContrato(db.Model):

    __tablename__ = 'dim_plantillas_contrato'

    id = db.Column(db.Integer,primary_key=True)

    nombre = db.Column(db.String(200),nullable=False)

    empresa_prestadora = db.Column(db.String(200), nullable=False)

    archivo = db.Column(db.String(500),nullable=False)

    descripcion = db.Column(db.String(500),nullable=False)

    activa = db.Column(db.Boolean,default=True)
