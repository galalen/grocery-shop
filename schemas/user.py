from marshmallow import Schema, fields, validate


class UserSchema(Schema):

    ROLE_CLIENT = 'client'
    ROLE_USER = 'user'

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    phonenumber = fields.Str(required=True)
    gender = fields.Str(required=True, validate=validate.OneOf(["M", "F"]))
    role = fields.Str(required=True, validate=validate.OneOf([ROLE_USER, ROLE_USER]))
