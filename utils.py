import bson
from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from db import db


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = db.users.find_one({'_id': bson.ObjectId(user_id)})
            if not user or (user and user['role'] != role):
                return {'error': 'Unauthorized access'}, 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
