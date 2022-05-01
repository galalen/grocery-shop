import csv
from datetime import datetime
from io import StringIO

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from schemas.product import ProductSchema, ReviewSchema
from utils import role_required
from db import db
from caching import cache

product_api = Blueprint("product", __name__)


@product_api.route("/", methods=["POST"])
@role_required("admin")
def upload_products():
    """
    Upload product to the database
    """
    upload_file = request.files["file"]
    if not upload_file:
        return {"error": "No file selected"}, 400

    cvs_data = StringIO(upload_file.read().decode()).read()

    rows = []
    reader = csv.reader(cvs_data.splitlines(), delimiter=",")
    # Skip the header
    header = next(reader)
    for row in reader:
        rows.append(dict(zip(header, row)))

    try:
        product_schema = ProductSchema()

        # cast data before saving to database
        for row in rows:
            row["price"] = float(row["price"])
            row["barcode"] = int(row["barcode"])
            row["available"] = row["available"] == "TRUE"
            product_schema.load(row)

        db.products.insert_many(rows)
    except Exception as e:
        return {"error": "Check file content and format"}, 400

    return {"message": "Products uploaded successfully"}, 201


@product_api.route("/review", methods=["POST"])
@role_required("client")
def add_review():
    """
    Add review to a product
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    data["userId"] = user_id

    try:
        review_schema = ReviewSchema()
        review_data = review_schema.load(data)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    product = db.products.find_one({"barcode": review_data["barcode"]})
    if not product:
        return {"error": "Product not found"}, 404

    review_data["createdAt"] = datetime.utcnow()
    db.reviews.insert_one(review_data)
    return {"message": "Review added successfully"}, 201


@product_api.route("/search", methods=["POST"])
@role_required("client")
@cache.cached(timeout=300)
def search_products():
    """
    Search for a product
    """
    query = request.args.get("searchText")
    page = request.args.get("page", 0)

    if not str(page).isnumeric():
        return {"error": "Page must be a number"}, 400
    page = int(page)

    # limit results to 10 per page
    limit = 10

    if query:
        count = db.products.count_documents({"$text": {"$search": query}})
        products = db.products.find({"$text": {"$search": query}}).sort("name", 1).skip(page * limit).limit(limit)
    else:
        count = db.products.count_documents({})
        products = db.products.find().sort("name", 1).skip(page * limit).limit(limit)

    # fetch latest two reviews with names
    limit_reviews = 2
    result = []
    for product in products:
        reviews = db.reviews.aggregate(
            [
                {"$match": {"barcode": product["barcode"]}},
                {"$lookup": {"from": "users", "localField": "userId", "foreignField": "_id", "as": "user"}},
                {"$sort": {"createdAt": -1}},
                {"$limit": limit_reviews},
            ]
        )

        product["reviews"] = [{"name": review["user"][0]["name"], "review": review["review"]} for review in reviews]
        result.append(product)

    products_schema = ProductSchema(many=True)
    data = products_schema.dump(result)
    return {"totalCount": count, "products": data}, 200
