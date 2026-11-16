from flask import Blueprint, jsonify

import report_service


report_bp = Blueprint("reports", __name__)


@report_bp.route("/reports/overdue", methods=["GET"])
def report_overdue():
    result = report_service.overdue_report()
    return jsonify(result)


@report_bp.route("/reports/summary", methods=["GET"])
def report_summary():
    result = report_service.summary_report()
    return jsonify(result)