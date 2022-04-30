import csv
from datetime import datetime
from io import StringIO
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from schemas.product import ProductSchema, ReviewSchema
from db import db


product_api = Blueprint('product', __name__)


@product_api.route('/', methods=['POST'])
@jwt_required()
def upload_products():
    """
    Upload product to the database
    """
    user_id = get_jwt_identity()
    upload_file = request.files['file']
    if not upload_file:
        return {'error': 'No file selected'}, 400

    cvs_data = StringIO(upload_file.read().decode()).read()

    rows = []
    reader = csv.reader(cvs_data.splitlines(), delimiter=',')
    # Skip the header
    header = next(reader)
    for row in reader:
        rows.append(dict(zip(header, row)))

    try:
        # cast data before saving to database
        for row in rows:
            row['price'] = float(row['price'])
            row['barcode'] = int(row['barcode'])
            row['available'] = row['available'] == 'TRUE'

        db.products.insert_many(rows)
    except Exception:
        return {'error': 'Verify file format'}, 400

    return {"message": "Products uploaded successfully"}, 201


@product_api.route('/review', methods=['POST'])
@jwt_required()
def add_review():
    """
    Add review to a product
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    data['userId'] = user_id

    try:
        review_schema = ReviewSchema()
        review_data = review_schema.load(data)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    product = db.products.find_one({'barcode': review_data['barcode']})
    if not product:
        return {'error': 'Product not found'}, 404

    review_data['createdAt'] = datetime.now()
    db.reviews.insert_one(review_data)
    return {'message': 'Review added successfully'}, 201
