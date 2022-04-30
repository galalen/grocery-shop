from marshmallow import Schema, fields, validate, ValidationError
from models.user import User
from schemas.fields import ObjectId


def phone_isdigit(value):
    if not value.isdigit():
        raise ValidationError('Must be numeric')


class UserSchema(Schema):

    _id = ObjectId(load_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    phonenumber = fields.Str(required=True, validate=validate.And(validate.Length(min=8), phone_isdigit))
    gender = fields.Str(required=True, validate=validate.OneOf([User.GENDER_MALE, User.GENDER_FEMALE]))
    role = fields.Str(required=True, validate=validate.OneOf([User.ROLE_CLIENT, User.ROLE_ADMIN]), load_only=True)


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
