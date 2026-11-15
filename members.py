
from flask import Blueprint, jsonify, request

import member_service


member_bp = Blueprint("members", __name__)


@member_bp.route("/members", methods=["GET"])
def list_members():
    result = member_service.list_members()
    return jsonify(result)


@member_bp.route("/members/<int:member_id>", methods=["GET"])
def get_member(member_id):
    result = member_service.get_member(member_id)

    if result is None:
        return jsonify({"error": "member not found"}), 404

    return jsonify(result)


@member_bp.route("/members", methods=["POST"])
def create_member():
    data = request.get_json(silent=True) or {}
    result, status_code = member_service.create_member(data)

    return jsonify(result), status_code


@member_bp.route("/members/<int:member_id>/loans", methods=["GET"])
def member_loans(member_id):
    result, status_code = member_service.get_member_loans(member_id)

    return jsonify(result), status_code
