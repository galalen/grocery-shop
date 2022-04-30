from marshmallow import Schema, fields
from schemas.fields import ObjectId


class ReviewSchema(Schema):

    _id = ObjectId(load_only=True)
    userId = ObjectId(required=True)
    barcode = fields.Int(required=True)
    review = fields.Str(required=True)
    createdAt = fields.DateTime(dump_only=True)


class NestedReviewSchema(Schema):

    name = fields.Str(required=True)
    review = fields.Str(required=True)


class ProductSchema(Schema):

    _id = ObjectId(load_only=True)
    name = fields.Str(required=True)
    barcode = fields.Int(required=True)
    brand = fields.Str(required=True)
    description = fields.Str(required=True)
    price = fields.Float(required=True)
    available = fields.Boolean(required=True)

    reviews = fields.Nested(NestedReviewSchema, many=True, dump_only=True, required=False)
