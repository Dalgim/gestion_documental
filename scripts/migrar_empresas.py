from app import db
from models import Proyecto, Empresa, Trabajador

# =========================================
# PASO 1: Crear empresas únicas
# =========================================
proyectos = Proyecto.query.all()

empresas_creadas = {}

for p in proyectos:

    nombre_empresa = getattr(p, "nom_empresa", None)

    if nombre_empresa:

        nombre_empresa = nombre_empresa.upper().strip()

        if nombre_empresa not in empresas_creadas:

            empresa = Empresa(
                nombre=nombre_empresa
            )

            db.session.add(empresa)
            db.session.flush()

            empresas_creadas[nombre_empresa] = empresa.id

db.session.commit()

# =========================================
# PASO 2: Asignar empresa a proyectos
# =========================================

proyectos = Proyecto.query.all()

for p in proyectos:

    if hasattr(p, "nom_empresa") and p.nom_empresa:

        nombre = p.nom_empresa.upper().strip()

        empresa = Empresa.query.filter_by(
            nombre=nombre
        ).first()

        if empresa:

            p.empresa_id = empresa.id

db.session.commit()

# =========================================
# PASO 3: Asignar empresa a trabajadores
# =========================================

trabajadores = Trabajador.query.all()

for t in trabajadores:

    if hasattr(t, "proyecto_id") and t.proyecto_id:

        proyecto = Proyecto.query.get(t.proyecto_id)

        if proyecto and proyecto.empresa_id:

            t.empresa_id = proyecto.empresa_id

db.session.commit()

print("Migración completada correctamente")