# Script que ejecutara el entorno flask
# importamos las librerias necesarias para el proyecto
from flask import Flask, render_template, request, redirect, send_file, jsonify, flash, url_for, session
from flask_login import login_manager, login_user, logout_user, login_required, current_user, LoginManager
from services.generador_documentos import generar_contrato, actualizar_contrato, fecha_letra
from models.models import db, Cliente, Proyecto, Contrato, Trabajador, Users, PlantillaContrato, Empresa
from werkzeug.security import check_password_hash
from flask_migrate import Migrate
from datetime import datetime
import secrets

app = Flask(__name__)

# Establecemos la configuracion de la base de datos y del cifrado del login
app.config[
    'SQLALCHEMY_DATABASE_URI'
] = 'sqlite:///C:\\Users\\gta\\Documents\\gestion_documental\\database\\database.db'

app.config[
    'SECRET_KEY'
] = secrets.token_hex(32)

# Generamos el login usando la libreria flask_login
login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'login'

db.init_app(app)
migrate = Migrate(app, db)
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(id):

    return Users.query.get(
        int(id)
    )

# Definimos una ruta para login 
@app.route(
    '/login',
    methods=['GET', 'POST']
)
def login():

    if request.method == 'POST':

        usuario = Users.query.filter_by(
            nombre_usuario=request.form[
                'user'
            ]
        ).first()

        if usuario and check_password_hash(
            usuario.contraseña,
            request.form['contraseña']
        ):

            login_user(
                usuario
            )

            return redirect(
                url_for('inicio')
            )

        flash(
            'Usuario o contraseña incorrectos'
        )

    return render_template(
        'login.html'
    )

# Definimos la ruta para el logout
@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(
        url_for('login')
    )

# Definimos como se conformara el site 
# usamos login_required ya que es necesario el inicio de sesion para visualizar la vista
# establecemos la primera ruta de inicio de la pagina
@app.route('/')
@login_required
def inicio():
    #return "Sistema de Gestión Documental NBIKA"
    #return render_template('index.html')
    return render_template('base.html')


# Definimos la ruta para el alta de clientes
# establecemos la pagina para el alta
@app.route('/clientes')
@login_required
def clientes():
    clientes = Cliente.query.all()

    return render_template(
        'cliente.html',
        clientes = clientes
    )

# definimos la seccion para el alta de clientes
@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    
    if request.method == 'POST':

        # obtenemos el nombre del cliente
        cliente=request.form['nombre_cliente']

        # Omitimos del nombre del cliente palabras que no son necesarias y dejar la nomenclatura
        # correcta, por ello se crea un diccionario para quitar las palabras innecesarias del nombre
        # de la empresa
        omitir = {
            "DE",
            "DEL",
            "LA",
            "LAS",
            "LOS",
            "Y",
            "E",
            "S.A.",
            "SA",
            "CV",
            "RL",
            "C.V.",
            "R.L."
        }

        # Armamos la nomenclatura
        iniciales = "".join(
            palabra[0]
            for palabra in cliente.upper().split()
            if palabra not in omitir
        )

        cliente = Cliente(
            nombre_cliente=request.form['nombre_cliente'],
            rfc=request.form['rfc'],
            representante=request.form['representante'],
            correo=request.form['correo'],
            dom_fiscal=request.form['dom_fiscal'],
            nomenclatura=iniciales
        )

        # Añadimos el dato de la lista "cliente" a la tabla dim_clientes de la BD
        # usamos "commit()" para ejecutar la instruccion "insert"
        db.session.add(cliente)
        db.session.commit()

        return redirect('/clientes')
    
    return render_template(
        'nuevo_cliente.html'
    )


# Establecemos la ruta inicial para la pagina de carga de servicios
@app.route('/proyectos')
@login_required
def proyectos():

    proyectos = Proyecto.query.all()
    #empresas = Empresa.query.all()

    return render_template(
        'servicios.html',
        proyectos = proyectos
    )

# Ruta para la generacion de los servicios 
@app.route('/proyectos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_proyecto():

    empresas = Empresa.query.all()

    if request.method == 'POST':

        proyecto = Proyecto(
            nombre_proyecto=request.form['nombre_proyecto'],
            folio_repse=request.form['folio_repse'],
            act_repse=request.form['act_repse'],
            tipo_servicio=request.form['tipo_servicio'],
            empresa_id=request.form['empresa_id']
        )

        db.session.add(proyecto)
        db.session.commit()

        print(proyecto)

        return redirect('/proyectos')

    return render_template(
        'nuevo_proyecto.html',
        empresas = empresas
    )



# Definimos la ruta para el alta de trabajadores
# establecemos la pagina para el alta
@app.route('/trabajadores')
@login_required
def trabajadores():
    trabajadores = Trabajador.query.all()

    proyectos = Proyecto.query.all()
    #empresas = Empresa.query.all()

    return render_template(
        'trabajador.html',
        trabajadores = trabajadores,
        proyectos = proyectos,
    )


# Ruta para la generacion de trabajadores 
@app.route('/trabajadores/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_trabajador():
    
    #proyectos = Proyecto.query.all()
    empresas = Empresa.query.all()

    if request.method == 'POST':

        trabajador = Trabajador(
            nombre_trabajador=request.form['nombre_trabajador'],
            curp=request.form['curp'],
            rfc=request.form['rfc'],
            nss=request.form['nss'],
            salario_base=request.form['salario_base'],
            actividades=request.form['actividades'],
            puesto=request.form['puesto'],
            empresa_id = request.form['empresa_id']
        )

        db.session.add(trabajador)
        db.session.commit()

        print(trabajador)

        return redirect('/trabajadores')

    return render_template(
        'nuevo_trabajador.html',
        #proyectos = proyectos
        empresas = empresas
    )


# Ruta para visualizar los contratos generados
@app.route('/contratos')
@login_required
def contratos():

    clientes = Cliente.query.order_by(
        Cliente.nombre_cliente
    ).all()

    proyectos = Proyecto.query.order_by(
        Proyecto.nombre_proyecto
    ).all()

    trabajadores = Trabajador.query.order_by(
        Trabajador.nombre_trabajador
    ).all()

    contratos = Contrato.query.order_by(
        Contrato.nom_empresa
    ).all()

    # usamos render template para cargar la pagina indicada con los datos 
    # que se requieren de la base de datos
    return render_template(
        'contrato.html',
        clientes=clientes,
        proyectos=proyectos,
        trabajadores=trabajadores,
        contratos=contratos
    )


# Vista para el formulario de nuevo contrato
@app.route(
    '/contratos/nuevo'
)
@login_required
def nuevo_contrato():

    clientes = Cliente.query.order_by(
        Cliente.nombre_cliente
    ).all()

    proyectos = Proyecto.query.order_by(
        Proyecto.nombre_proyecto
    ).distinct().all()

    trabajadores = Trabajador.query.order_by(
        Trabajador.nombre_trabajador
    ).all()

    return render_template(
        'nuevo_contrato.html',
        clientes=clientes,
        proyectos=proyectos,
        trabajadores=trabajadores
        #empresas_prestadoras=empresas_prestadoras
    )

# Aqui se genera el contrato de forma habitual
@app.route(
    '/contratos/generar',
    methods=['GET','POST']
)
@login_required
def generar_contrato_web():

    if request.method == 'POST':

        cliente = Cliente.query.get_or_404(
            request.form['cliente_id']
        )

        proyecto = Proyecto.query.get_or_404(
            request.form['proyecto_id']
        )

        fecha_inicio = datetime.strptime(
            request.form['fecha_inicio'],
            '%Y-%m-%d'
        )

        fecha_fin = datetime.strptime(
            request.form['fecha_fin'],
            '%Y-%m-%d'
        )

        meses = (
            (fecha_fin.year - fecha_inicio.year) * 12
            + (fecha_fin.month - fecha_inicio.month)
        )

        if fecha_fin.day >= fecha_inicio.day:
            meses += 1

        ids_trabajadores = request.form.getlist(
            'trabajadores'
        )

        trabajadores_db = Trabajador.query.filter(
            Trabajador.id.in_(ids_trabajadores)
        ).all()

        trabajadores = []

        for t in trabajadores_db:

            trabajadores.append({

                "nombre": t.nombre_trabajador.upper(),
                "nss": t.nss,
                "curp": t.curp.upper(),
                "salario": t.salario_base,
                "actividades": t.actividades.upper(),
                "puesto": t.puesto.upper()

            })

        contexto = {

            "NOMENCLATURA": cliente.nomenclatura.upper(),

            "CLIENTE": cliente.nombre_cliente.upper(),

            "RFC": cliente.rfc.upper(),

            "DOM_FISCAL": cliente.dom_fiscal.upper(),

            "REPRESENTANTE": cliente.representante.upper(),

            "PROYECTO": proyecto.nombre_proyecto.upper(),

            "TIPO_SERVICIO": proyecto.tipo_servicio.upper(),
            
            "EMPRESA_SERVICIO": proyecto.empresa.nombre.upper(),

            "MONTO": request.form['monto'],

            "VIGENCIA": f"{meses} MESES",

            "INICIO":
                #fecha_inicio.strftime("%d/%m/%Y"),
                fecha_letra(fecha_inicio),

            "FIN": fecha_fin.strftime("%d/%m/%Y"),

            "FORMA_PAGO": request.form['forma_pago'],

            "LUGAR_FIRMA": request.form['lugar_firma'].upper(),

            "trabajadores": trabajadores
        }

        archivo = generar_contrato(
            #plantilla,
            contexto
        )

        nuevo_contrato = Contrato(
            cliente_id = cliente.id,
            proyecto_id = proyecto.id,
            nom_empresa = proyecto.empresa.nombre,
            nom_cliente = cliente.nombre_cliente,
            monto = request.form['monto'],
            forma_pago = request.form['forma_pago'],
            fecha_inicio = datetime.strptime(
                request.form['fecha_inicio'],
                '%Y-%m-%d'
            ).date(),
            fecha_fin = datetime.strptime(
                request.form['fecha_fin'],
                '%Y-%m-%d'
            ).date(),
            vigencia = f"{meses} Meses"
        )

        db.session.add(nuevo_contrato)
        db.session.commit()

        # Generar documento
        ruta = actualizar_contrato(
            contexto
        )

        # Guardar ruta
        nuevo_contrato.archivo_generado = ruta
        db.session.commit()

        return send_file(
            archivo,
            as_attachment=True
        )

    return redirect('/contratos')

# esta ruta sirve para conectar con el javascript
@app.route('/proyectos/<int:id>/trabajadores')
@login_required
def trabajadores_por_proyecto(id):

    proyecto = Proyecto.query.get_or_404(id)

    trabajadores = Trabajador.query.filter_by(
        empresa_id=proyecto.empresa_id
    ).order_by(
        Trabajador.nombre_trabajador
    ).all()

    return jsonify([
        {
            "id": t.id,
            "nombre": t.nombre_trabajador
        }
        for t in trabajadores
    ])


# Ruta para obtener las plantillas de contrato por empresa
@app.route('/api/plantillas')
@login_required
def api_plantillas():

    empresa = request.args.get('empresa')

    print(empresa)

    plantillas = PlantillaContrato.query.filter_by(
        empresa_prestadora=empresa,
        activa=True
    ).order_by(
        PlantillaContrato.nombre
    ).all()

    print(plantillas)

    return jsonify([
        {
            'id': p.id,
            'nombre': p.nombre
        }
        for p in plantillas
    ])

# Ruta para listar las plantillas de contrato guardadas
@app.route('/plantillas')
@login_required
def listar_plantillas():

    plantillas = PlantillaContrato.query.order_by(
        PlantillaContrato.nombre
    ).all()

    return render_template(
        'plantillas.html',
        plantillas=plantillas
    )


# Ruta para guardar las plantillas de contrato por empresa
@app.route(
    '/plantillas/nueva',
    methods=['GET', 'POST']
)
@login_required
def nueva_plantilla():

    if request.method == 'POST':

        plantilla = PlantillaContrato(

            nombre=request.form[
                'nombre'
            ].upper(),

            empresa_prestadora=request.form[
                'empresa_prestadora'
            ].upper(),

            archivo=request.form[
                'archivo'
            ],

            descripcion=request.form.get(
                'descripcion'
            )

        )

        db.session.add(
            plantilla
        )

        db.session.commit()

        return redirect(
            url_for(
                'listar_plantillas'
            )
        )

    return render_template(
        '/nueva_plantilla.html'
    )

# Ruta para listar las empresas
@app.route('/empresas')
@login_required
def empresas():

    empresas = Empresa.query.order_by(
        Empresa.nombre
    ).all()

    return render_template(
        'listar_empresas.html',
        empresas=empresas
    )

# Ruta para crear nueva empresa
@app.route(
    '/empresas/nueva',
    methods=['GET', 'POST']
)
@login_required
def nueva_empresa():

    if request.method == 'POST':

        empresa = Empresa(

            nombre=request.form['nombre'].upper(),

            rfc=request.form.get('rfc','').upper(),

            representante=request.form.get('representante','').upper(),

            domicilio=request.form.get('domicilio','').upper(),

            correo=request.form.get('correo','').lower(),

            telefono=request.form.get('telefono','')

        )

        db.session.add(empresa)
        db.session.commit()

        flash(
            'Empresa creada correctamente',
            'success'
        )

        return redirect(
            url_for('empresas')
        )

    return render_template(
        'nueva_empresa.html'
    )


# ======================================================================================
# Seccion para editar clientes, trabajadores, plantillas, servicios, contratos, empresas
# ======================================================================================


# ==========================================
# Editar Trabajador
# ==========================================
@app.route(
    '/trabajadores/editar/<int:id>',
    methods=['GET', 'POST']
)
@login_required
def editar_trabajador(id):

    trabajador = Trabajador.query.get_or_404(id)

    empresas = Empresa.query.all()

    if request.method == 'POST':

        trabajador.nombre_trabajador = request.form['nombre_trabajador'].upper()
        trabajador.curp = request.form['curp'].upper()
        trabajador.nss = request.form['nss']
        trabajador.puesto = request.form['puesto'].upper()
        trabajador.actividad = request.form['actividad'].upper()
        trabajador.salario_base = request.form['salario_base']
        trabajador.empresa_id = request.form['empresa_id']
        db.session.commit()

        flash(
            'Trabajador actualizado correctamente',
            'success'
        )

        return redirect(
            url_for('trabajadores')
        )

    return render_template(
        'editar_trabajador.html',
        trabajador=trabajador,
        empresas=empresas
    )


# ==========================================
# Eliminar Trabajador
# ==========================================
@app.route(
    '/trabajadores/eliminar/<int:id>',
    methods=['POST']
)
@login_required
def eliminar_trabajador(id):

    trabajador = Trabajador.query.get_or_404(id)

    try:

        db.session.delete(trabajador)
        db.session.commit()

        flash(
            'Trabajador eliminado correctamente',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        flash(
            str(e),
            'danger'
        )

    return redirect(
        url_for('trabajadores')
    )


# ==========================================
# Editar plantilla
# ==========================================
@app.route(
    '/plantillas/editar/<int:id>',
    methods=['GET', 'POST']
)
@login_required
def editar_plantilla(id):

    plantilla = PlantillaContrato.query.get_or_404(
        id
    )

    if request.method == 'POST':

        plantilla.nombre = request.form[
            'nombre'
        ].upper()

        plantilla.empresa_prestadora = request.form[
            'empresa_prestadora'
        ].upper()

        plantilla.archivo = request.form[
            'archivo'
        ]

        plantilla.descripcion = request.form.get(
            'descripcion'
        )

        db.session.commit()

        flash(
            'Plantilla actualizada'
        )

        return redirect(
            url_for(
                'listar_plantillas'
            )
        )

    return render_template(
        'editar_plantilla.html',
        plantilla=plantilla
    )



# ==========================================
# Eliminar plantilla
# ==========================================
@app.route(
    '/plantillas/eliminar/<int:id>',
    methods=['POST']
)
@login_required
def eliminar_plantilla(id):

    plantilla = PlantillaContrato.query.get_or_404(
        id
    )

    db.session.delete(
        plantilla
    )

    db.session.commit()

    flash(
        'Plantilla eliminada'
    )

    return redirect(
        url_for(
            'listar_plantillas'
        )
    )


# ==========================================
# Editar Cliente
# ==========================================
@app.route(
    '/clientes/editar/<int:id>',
    methods=['GET', 'POST']
)
@login_required
def editar_cliente(id):

    cliente = Cliente.query.get_or_404(id)

    if request.method == 'POST':

        cliente.nombre_cliente = request.form[
            'nombre_cliente'
        ].upper()

        cliente.rfc = request.form[
            'rfc'
        ].upper()

        cliente.representante = request.form[
            'representante'
        ].upper()

        cliente.dom_fiscal = request.form[
            'dom_fiscal'
        ].upper()

        cliente.correo = request.form[
            'correo'
        ].lower()

        db.session.commit()

        flash(
            'Cliente actualizado correctamente.',
            'success'
        )

        return redirect(
            url_for(
                'listar_clientes'
            )
        )

    return render_template(
        'editar_cliente.html',
        cliente=cliente
    )

# ==========================================
# Eliminar Cliente
# ==========================================
@app.route(
    '/clientes/eliminar/<int:id>',
    methods=['POST']
)
@login_required
def eliminar_cliente(id):

    cliente = Cliente.query.get_or_404(id)

    try:
        db.session.delete(cliente)
        db.session.commit()
        flash(
            'Cliente eliminado correctamente.',
            'success'
        )

    except Exception:
        db.session.rollback()
        flash(

            'No fue posible eliminar el cliente. '
            'Probablemente tiene proyectos o contratos asociados.',
            'danger'
        )

    return redirect(
        url_for(
            'listar_clientes'
        )
    )


# ==========================================
# Editar Servicio
# ==========================================
@app.route(
    '/proyectos/editar/<int:id>',
    methods=['GET', 'POST']
)
@login_required
def editar_servicio(id):

    proyecto = Proyecto.query.get_or_404(id)

    empresas = Empresa.query.all()

    if request.method == 'POST':

        proyecto.nombre_proyecto = request.form[
            'nombre_proyecto'
        ].upper()

        proyecto.folio_repse = request.form[
            'folio_repse'
        ].upper()

        proyecto.act_repse = request.form[
            'act_repse'
        ].upper()

        proyecto.nom_empresa = request.form[
            'nom_empresa'
        ].upper()

        proyecto.tipo_servicio = request.form[
            'tipo_servicio'
        ].upper()

        db.session.commit()

        flash(
            'Servicio actualizado correctamente.',
            'success'
        )

        return redirect(
            url_for(
                'proyectos'
            )
        )

    return render_template(

        'editar_servicios.html',
        empresas = empresas,
        proyecto=proyecto

    )

# ==========================================
# Eliminar Servicio
# ==========================================

@app.route(
    '/proyectos/eliminar/<int:id>',
    methods=['POST']
)
@login_required
def eliminar_servicio(id):

    try:

        servicio = Proyecto.query.get_or_404(id)

        # ❌ NO tocar trabajadores

        db.session.delete(servicio)
        db.session.commit()

        flash('Servicio eliminado correctamente', 'success')

    except Exception as e:

        db.session.rollback()

        print("ERROR REAL:", e)

        flash('Error al eliminar el servicio', 'danger')

    return redirect(url_for('proyectos'))


# ==========================================
# Editar empresa
# ==========================================
@app.route(
    '/empresas/editar/<int:id>',
    methods=['GET', 'POST']
)
@login_required
def editar_empresa(id):

    empresa = Empresa.query.get_or_404(id)

    if request.method == 'POST':

        empresa.nombre = request.form['nombre'].upper()
        empresa.rfc = request.form.get('rfc','').upper()
        empresa.representante = request.form.get('representante','').upper()
        empresa.domicilio = request.form.get('domicilio','').upper()
        empresa.correo = request.form.get('correo','').lower()
        empresa.telefono = request.form.get('telefono','')

        db.session.commit()

        flash(
            'Empresa actualizada correctamente',
            'success'
        )

        return redirect(
            url_for('empresas')
        )

    return render_template(
        'editar_empresa.html',
        empresa=empresa
    )


# ==========================================
# Eliminar empresa
# ==========================================
@app.route(
    '/empresas/eliminar/<int:id>',
    methods=['POST']
)
@login_required
def eliminar_empresa(id):

    empresa = Empresa.query.get_or_404(id)

    try:

        # Validaciones de seguridad
        if empresa.proyectos:
            flash(
                'No se puede eliminar: tiene proyectos asociados',
                'warning'
            )
            return redirect(url_for('empresas'))

        if len(empresa.trabajadores) > 0:
            flash(
                'No se puede eliminar: tiene trabajadores asociados',
                'warning'
            )
            return redirect(url_for('empresas'))

        db.session.delete(empresa)
        db.session.commit()

        flash(
            'Empresa eliminada correctamente',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        flash(
            str(e),
            'danger'
        )

    return redirect(
        url_for('empresas')
    )


if __name__ == '__main__':
    app.run(debug=True)