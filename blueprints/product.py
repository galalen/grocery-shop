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
        product_schema = ProductSchema()

        # cast data before saving to database
        for row in rows:
            row['price'] = float(row['price'])
            row['barcode'] = int(row['barcode'])
            row['available'] = row['available'] == 'TRUE'
            product_schema.load(row)

        db.products.insert_many(rows)
    except Exception as e:
        return {'error': 'Check file content and format'}, 400

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


@product_api.route('/search', methods=['POST'])
def search_products():
    """
    Search for a product
    """
    query = request.args.get('searchText')
    page = int(request.args.get('page', 0))
    limit = 10

    if query:
        count = db.products.count_documents({'$text': {'$search': query}})
        pipline = [
            {"$match": {"$text": {'$search': query}}},
            {"$lookup": {"from": "reviews", "localField": "barcode", "foreignField": "barcode", "as": "reviews"}},
            {"$sort": {"name": 1}},
            {"$skip": page * limit},
            {"$limit": limit}
        ]
        products = db.products.aggregate(pipline)
    else:
        count = db.products.count_documents({})
        pipline = [
            {"$lookup": {"from": "reviews", "localField": "barcode", "foreignField": "barcode", "as": "reviews"}},
            {"$sort": {"name": 1}},
            {"$skip": page * limit},
            {"$limit": limit}
        ]
        products = db.products.aggregate(pipline)

    # fetch reviews names
    result = []
    for product in products:
        for review in product['reviews']:
            user = db.users.find_one({'_id': review['userId']})
            review['name'] = user['name']
        result.append(product)

    products_schema = ProductSchema(many=True)
    data = products_schema.dump(result)
    return {"totalCount": count, "products": data}, 200
