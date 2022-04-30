from marshmallow import Schema, fields
from schemas.fields import ObjectId


class ProductSchema(Schema):

    _id = ObjectId(dump_only=True)
    name = fields.Str(required=True)
    barcode = fields.Int(required=True)
    description = fields.Str(required=True)
    price = fields.Float(required=True)
    available = fields.Boolean(required=True)
