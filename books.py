
from flask import Blueprint, jsonify, request

import book_service


book_bp = Blueprint("books", __name__)


@book_bp.route("/books", methods=["GET"])
def list_books():
    available_only = request.args.get("available") == "true"

    books = book_service.list_books(available_only)

    return jsonify(books)


@book_bp.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = book_service.get_book(book_id)

    if book is None:
        return jsonify({"error": "book not found"}), 404

    return jsonify(book)


@book_bp.route("/books", methods=["POST"])
def create_book():
    data = request.get_json(silent=True) or {}

    result, status = book_service.create_book(data)

    return jsonify(result), status


@book_bp.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    result, status = book_service.delete_book(book_id)

    if status == 204:
        return "", 204

    return jsonify(result), status
