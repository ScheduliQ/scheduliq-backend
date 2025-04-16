# generate_pdf.py

from io import BytesIO
import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Import the report calculation functions
from utils.reports_calculations import (
    get_all_schedules_from_db,
    calculate_employee_shift_count,
    calculate_role_required_vs_assigned,
    calculate_average_employees_per_shift,
    calculate_shifts_by_type
)

# Import manager settings
from models.manager_settings_model import get_manager_settings


def generate_report_pdf():
    """
    Generates an advanced, modern-styled PDF report (2025 level) that combines system analytics
    with manager settings. The report is laid out with clean fonts, refined colors, and
    strategically placed key insights to maximize clarity.
    
    The report includes:
      - A modern title page with a generation timestamp.
      - An Executive Summary with key metrics.
      - A Manager Settings section displaying system configuration details.
      - A Report Analytics section featuring detailed tables on employee shifts,
        role coverage, and shifts by type.
    
    :return: A BytesIO object containing the generated PDF ready for download.
    """
    # Retrieve data using the helper functions
    schedules = get_all_schedules_from_db()
    employee_shift_counts = calculate_employee_shift_count(schedules)
    role_coverage = calculate_role_required_vs_assigned(schedules)
    average_employees = calculate_average_employees_per_shift(schedules)
    shifts_by_type = calculate_shifts_by_type(schedules)
    manager_settings = get_manager_settings()

    # Compute additional insights
    total_employees = len(employee_shift_counts)
    total_shifts = sum(employee_shift_counts.values())
    avg_shifts_per_employee = total_shifts / total_employees if total_employees else 0
    max_shifts_employee = max(employee_shift_counts.items(), key=lambda x: x[1]) if employee_shift_counts else ("N/A", 0)
    
    # Create an in-memory buffer for the PDF
    buffer = BytesIO()

    # Set up the document (A4 size with custom margins)
    doc = SimpleDocTemplate(buffer,
                            pagesize=A4,
                            rightMargin=50,
                            leftMargin=50,
                            topMargin=50,
                            bottomMargin=50,
                            title="Analytics Report")

    # Load and customize the stylesheet for a modern look
    styles = getSampleStyleSheet()
    # Title style
    styles.add(ParagraphStyle(
        name='MainTitle',
        alignment=1,
        fontSize=28,
        leading=32,
        spaceAfter=20,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2C3E50')  # Dark slate
    ))
    # Subtitle style (for timestamps and section subtitles)
    styles.add(ParagraphStyle(
        name='SubTitle',
        alignment=1,
        fontSize=14,
        leading=18,
        spaceBefore=4,
        spaceAfter=12,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#34495E')
    ))
    # Section header style
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontSize=16,
        leading=20,
        spaceBefore=16,
        spaceAfter=8,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2980B9')
    ))
    # Clone BodyText to our own custom style so as not to conflict
    custom_body = styles["BodyText"].clone('CustomBodyText')
    custom_body.fontSize = 12
    custom_body.leading = 16
    custom_body.spaceBefore = 4
    custom_body.spaceAfter = 4
    styles.add(custom_body)
    # Insight style for key statements in the report
    styles.add(ParagraphStyle(
        name='InsightText',
        fontSize=12,
        leading=16,
        spaceBefore=2,
        spaceAfter=6,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor('#7F8C8D')
    ))

    elements = []

    # ---------------- Title & Introduction ----------------
    elements.append(Paragraph("Advanced Shift Analytics Report", styles['MainTitle']))
    elements.append(Paragraph(f"Report generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['SubTitle']))
    elements.append(Spacer(1, 12))

    # ---------------- Executive Summary ----------------
    elements.append(Paragraph("Executive Summary", styles['SectionHeader']))

    # Create a summary table with key metrics
    summary_data = [
        ["Metric", "Value"],
        ["Total Employees", total_employees],
        ["Total Scheduled Shifts", total_shifts],
        ["Average Shifts per Employee", f"{avg_shifts_per_employee:.1f}"],
        ["Number of Roles", len(role_coverage)],
        ["Average Employees per Shift", f"{average_employees['average']:.1f}"],
        ["Shift Types Available", len(shifts_by_type)]
    ]
    summary_table = Table(summary_data, colWidths=[doc.width/2 - 20, doc.width/2 - 20])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2980B9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Add key insight paragraphs below the summary
    key_insights = [
        f"The highest workload is for {max_shifts_employee[0]} with {max_shifts_employee[1]} shifts.",
        f"Review staffing for roles with low coverage to ensure proper service levels."
    ]
    for insight in key_insights:
        elements.append(Paragraph(insight, styles['InsightText']))
    elements.append(Spacer(1, 15))
    elements.append(PageBreak())

    # ---------------- Manager Settings Section ----------------
    elements.append(Paragraph("Manager Settings & Configuration", styles['SectionHeader']))

    # Basic Manager Settings Table (modern look)
    manager_info = [
        ["Setting", "Value"],
        ["Shifts Per Day", manager_settings.get("shifts_per_day", "N/A")],
        ["Shift Names", ", ".join(manager_settings.get("shift_names", []))],
        ["Max Consecutive Shifts", manager_settings.get("max_consecutive_shifts", "N/A")],
        ["Work Days", ", ".join(manager_settings.get("work_days", []))],
        ["Min Employees per Shift", manager_settings.get("min_max_employees_per_shift", {}).get("min", "N/A")],
        ["Max Employees per Shift", manager_settings.get("min_max_employees_per_shift", {}).get("max", "N/A")],
        ["Total Required Shifts", manager_settings.get("required_shifts", "N/A")]
    ]
    basic_table = Table(manager_info, colWidths=[doc.width/2 - 20, doc.width/2 - 20])
    basic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
        ('GRID', (0, 0), (-1, -1), 0.8, colors.HexColor('#BDC3C7')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(basic_table)
    elements.append(Spacer(1, 20))

    # Roles per Shift Configuration with refined styling
    elements.append(Paragraph("Roles per Shift Configuration", styles['SectionHeader']))
    roles_per_shift = manager_settings.get("roles_per_shift", {})
    for shift_name, roles in roles_per_shift.items():
        elements.append(Paragraph(f"{shift_name} Shift", styles['CustomBodyText']))
        role_data = [["Role", "Required Count"]]
        for role, count in roles.items():
            role_data.append([role.capitalize(), count])
        role_table = Table(role_data, colWidths=[doc.width/2 - 20, doc.width/2 - 20])
        role_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7F8C8D')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
            ('GRID', (0, 0), (-1, -1), 0.8, colors.HexColor('#BDC3C7')),
        ]))
        elements.append(role_table)
        elements.append(Spacer(1, 12))
    elements.append(PageBreak())

    # ---------------- Report Analytics Section ----------------
    elements.append(Paragraph("Report Analytics", styles['SectionHeader']))

    # Average Employees per Shift
    elements.append(Paragraph(f"Average Employees per Shift: {average_employees['average']}", styles['CustomBodyText']))
    elements.append(Spacer(1, 12))

    # Employee Shift Counts Table
    elements.append(Paragraph("Employee Shift Counts", styles['SectionHeader']))
    emp_data = [["Employee", "Shift Count"]]
    for employee, count in employee_shift_counts.items():
        emp_data.append([employee, count])
    emp_table = Table(emp_data, colWidths=[doc.width*0.65, doc.width*0.35])
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2980B9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#D6EAF8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#AED6F1')),
    ]))
    elements.append(emp_table)
    elements.append(Spacer(1, 12))

    # Role Coverage Table with computed coverage percentage
    elements.append(Paragraph("Role Coverage", styles['SectionHeader']))
    role_cov_data = [["Role", "Actual", "Required", "Coverage (%)"]]
    for role, data in role_coverage.items():
        actual = data.get("actual", 0)
        required = data.get("required", 0)
        coverage = round((actual / required * 100), 1) if required > 0 else 100
        role_cov_data.append([role.capitalize(), actual, required, f"{coverage}%"])
    role_cov_table = Table(role_cov_data, colWidths=[doc.width*0.25]*4)
    role_cov_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E9F7EF')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#A9DFBF')),
    ]))
    elements.append(role_cov_table)
    elements.append(Spacer(1, 12))

    # Shifts by Type Table
    elements.append(Paragraph("Shifts by Type", styles['SectionHeader']))
    shifts_data = [["Shift Type", "Count"]]
    for shift_type, count in shifts_by_type.items():
        shifts_data.append([shift_type.capitalize(), count])
    shifts_table = Table(shifts_data, colWidths=[doc.width*0.65, doc.width*0.35])
    shifts_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C0392B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FADBD8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#F5B7B1')),
    ]))
    elements.append(shifts_table)
    elements.append(Spacer(1, 12))

    # ---------------- Footer & Page Numbering ----------------
    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        footer_text = f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        canvas.drawString(50, 30, footer_text)
        canvas.drawRightString(A4[0] - 50, 30, f"Page {doc.page}")
        canvas.restoreState()

    # Build the PDF document with the footer callback
    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)
    return buffer
