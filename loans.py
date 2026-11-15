from flask import Blueprint, jsonify, request
import loan_service

loan_bp = Blueprint("loans", __name__)

@loan_bp.route("/loans", methods=["GET"])
def list_loans():
    overdue_only = request.args.get("overdue") == "true"
    result = loan_service.list_loans(overdue_only)
    return jsonify(result)


@loan_bp.route("/loans/<int:loan_id>", methods=["GET"])
def get_loan(loan_id):
    result, status_code = loan_service.get_loan(loan_id)
    return jsonify(result), status_code


@loan_bp.route("/loans", methods=["POST"])
def create_loan():
    data = request.get_json(silent=True) or {}
    result, status_code = loan_service.create_loan(data)
    return jsonify(result), status_code


@loan_bp.route("/loans/<int:loan_id>/return", methods=["POST"])
def return_book(loan_id):
    result, status_code = loan_service.return_book(loan_id)
    return jsonify(result), status_code


@loan_bp.route("/loans/<int:loan_id>/renew", methods=["POST"])
def renew_loan(loan_id):
    result, status_code = loan_service.renew_loan(loan_id)
    return jsonify(result), status_code


@loan_bp.route("/loans/<int:loan_id>/pay-fine", methods=["POST"])
def pay_fine(loan_id):
    result, status_code = loan_service.pay_fine(loan_id)
    return jsonify(result), status_code
