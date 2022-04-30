import os
from collections import OrderedDict
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid


client = MongoClient(os.getenv("MONGO_URI"))
db = client.grocery


def create_collection(collection_name, collection_schema):
    validator = {"$jsonSchema": {"bsonType": "object", "properties": {}}}
    required = []

    for field_key in collection_schema:
        field = collection_schema[field_key]
        properties = {"bsonType": field["type"]}
        minimum = field.get("minlength")
        maximum = field.get("maxlength")
        enum = field.get("enum")

        if type(minimum) == int:
            properties["minimum"] = minimum

        if type(maximum) == int:
            properties["maximum"] = maximum

        if type(enum) == list:
            properties["enum"] = enum

        if field.get("required") is True:
            required.append(field_key)

        validator["$jsonSchema"]["properties"][field_key] = properties

    if len(required) > 0:
        validator["$jsonSchema"]["required"] = required

    query = [("collMod", collection_name), ("validator", validator)]

    try:
        db.create_collection(collection_name)
    except CollectionInvalid:
        pass

    db.command(OrderedDict(query))


def init_db():
    user_schema = {
        "name": {
            "type": "string",
            "required": True,
        },
        "email": {
            "type": "string",
            "required": True,
        },
        "phonenumber": {
            "type": "string",
            "required": True,
            "minlength": 8,
        },
        "role": {
            "type": "string",
            "required": True,
            "enum": ["admin", "client"],
        },
        "gender": {"type": "string", "required": True, "enum": ["F", "M"]},
    }

    product_schema = {
        "name": {
            "type": "string",
            "required": True,
        },
        "brand": {
            "type": "string",
            "required": True,
        },
        "barcode": {
            "type": "number",
            "required": True,
        },
        "description": {
            "type": "string",
            "required": True,
        },
        "price": {
            "type": "number",
            "required": True,
        },
        "available": {
            "type": "bool",
            "required": True,
        },
    }

    review_schema = {
        "userId": {
            "type": "objectId",
            "required": True,
        },
        "barcode": {
            "type": "number",
            "required": True,
        },
        "review": {
            "type": "string",
            "required": True,
        },
        "createdAt": {
            "type": "date",
            "required": True,
        },
    }

    create_collection("users", user_schema)
    create_collection("products", product_schema)
    create_collection("reviews", review_schema)

    db.products.create_index("barcode", unique=True)
    db.products.create_index([("name", "text"), ("brand", "text")])
