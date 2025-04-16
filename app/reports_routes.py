# app/reports_routes.py

from flask import Blueprint, jsonify, send_file
from utils.generate_pdf import generate_report_pdf
from utils.reports_calculations import get_all_schedules_from_db, calculate_employee_shift_count,calculate_role_required_vs_assigned,calculate_average_employees_per_shift,calculate_shifts_by_type
reports_api = Blueprint("reports_api", __name__)

@reports_api.route("/general", methods=["GET"])
def general_reports():
    try:
        schedules = get_all_schedules_from_db()
        employee_shift_counts = calculate_employee_shift_count(schedules)
        role_coverage = calculate_role_required_vs_assigned(schedules)
        average_employees_per_shift = calculate_average_employees_per_shift(schedules)
        shifts_by_type = calculate_shifts_by_type(schedules)
        result = {
            "employee_shift_count": employee_shift_counts,
            "role_coverage": role_coverage,
            "average_employees_per_shift": average_employees_per_shift,
            "shifts_by_type": shifts_by_type
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reports_api.route("/export_pdf", methods=["GET"])
def export_pdf():
    pdf_buffer = generate_report_pdf()
    return send_file(pdf_buffer, as_attachment=True, download_name="report.pdf", mimetype="application/pdf")