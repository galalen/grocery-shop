from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import ValidationError
from schemas.user import UserSchema, LoginSchema
from db import db

user_api = Blueprint('user_api', __name__)


@user_api.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    """
    user_schema = UserSchema()
    try:
        user_data = user_schema.load(request.get_json())
    except ValidationError as err:
        return {"errors": err.messages}, 400

    user_data['password'] = generate_password_hash(user_data['password'])
    db.users.insert_one(user_data)
    return {"message": "User created successfully."}, 201


@user_api.route('/login', methods=['POST'])
def login():
    """
    Log in a user.
    """
    user_schema = LoginSchema()
    try:
        user_data = user_schema.load(request.get_json())
    except ValidationError as err:
        return {"errors": err.messages}, 400

    user = db.users.find_one({'email': user_data['email']})
    if user and check_password_hash(user['password'], user_data['password']):
        access_token = create_access_token(identity=str(user['_id']), fresh=True)
        refresh_token = create_refresh_token(identity=str(user['_id']))

        return (
            {
                "message": "User logged in successfully",
                "data":
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token
                    }
            },
            200,
        )
    return {"error": "Invalid email or password."}, 401

