from functools import wraps
from flask_login import current_user
from flask import abort

# Creamos un decorador para poder bloquear accesos por roles de usuario
def roles_requeridos(*roles):

    def decorator(func):

        @wraps(func)
        def decorated_function(*args, **kwargs):

            if current_user.rol not in roles:
                abort(403)

            return func(*args, **kwargs)

        return decorated_function

    return decorator