import bson
from marshmallow import ValidationError, fields, missing


class ObjectId(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return bson.ObjectId(value)
        except Exception:
            raise ValidationError("invalid ObjectId `%s`" % value)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return missing
        return str(value)
