from app import app
from models.models import db, Users
from werkzeug.security import generate_password_hash


with app.app_context():

    usuario = Users(

        nombre='Dalet Gimel Benitez Ramos',
        nombre_usuario='admin',
        contraseña=generate_password_hash(
            'Admin123'
        ),
        rol = 'ADMINISTRADOR' 

    )

    db.session.add(usuario)

    db.session.commit()

    print(
        'Usuario creado'
    )