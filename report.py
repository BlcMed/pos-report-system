"""
Generate PDF report from analyzed data.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
from io import BytesIO
import config


def create_header(styles, report_data):
    """Create report header."""
    elements = []

    # Title
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=6,
        alignment=TA_CENTER,
    )

    elements.append(Paragraph(config.RESTAURANT_NAME, title_style))

    # Subtitle
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=16,
        textColor=colors.HexColor("#666666"),
        spaceAfter=12,
        alignment=TA_CENTER,
    )

    period_start = report_data["period"]["start_date"].strftime("%B %Y")
    elements.append(
        Paragraph(f"{config.REPORT_TITLE} - {period_start}", subtitle_style)
    )

    elements.append(Spacer(1, 0.3 * inch))

    return elements


def create_summary_section(report_data):
    """Create executive summary section."""
    elements = []

    # Section title
    elements.append(
        Paragraph("<b>EXECUTIVE SUMMARY</b>", getSampleStyleSheet()["Heading2"])
    )
    elements.append(Spacer(1, 0.1 * inch))

    inv_metrics = report_data["invoices"]

    # Summary table
    summary_data = [
        ["Total Revenue", f"{inv_metrics['total_revenue']:,.2f}"],
        ["Total Transactions", f"{inv_metrics['total_transactions']:,}"],
        ["Average Transaction", f"{inv_metrics['average_transaction']:.2f}"],
        ["Total VAT Collected", f"{inv_metrics['total_vat']:.2f}"],
    ]

    # Add growth if available
    if "growth" in report_data and report_data["growth"] is not None:
        growth = report_data["growth"]
        arrow = "↑" if growth > 0 else "↓"
        summary_data.append(["Growth vs Previous Month", f"{growth:+.1f}% {arrow}"])

    summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f5f5")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.white),
            ]
        )
    )

    elements.append(summary_table)
    elements.append(Spacer(1, 0.3 * inch))

    return elements


def create_payment_section(report_data):
    """Create payment breakdown section."""
    elements = []

    elements.append(
        Paragraph("<b>PAYMENT BREAKDOWN</b>", getSampleStyleSheet()["Heading2"])
    )
    elements.append(Spacer(1, 0.1 * inch))

    payment_data = [["Payment Method", "Transactions", "Amount", "Percentage"]]

    total_amount = report_data["invoices"]["total_revenue"]

    for method, amount in report_data["invoices"]["payment_breakdown"][
        "amounts"
    ].items():
        count = report_data["invoices"]["payment_breakdown"]["counts"].get(method, 0)
        percentage = (amount / total_amount * 100) if total_amount > 0 else 0
        payment_data.append(
            [method, f"{count:,}", f"{amount:,.2f}", f"{percentage:.1f}%"]
        )

    payment_table = Table(
        payment_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch, 1 * inch]
    )
    payment_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a4a4a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    elements.append(payment_table)
    elements.append(Spacer(1, 0.3 * inch))

    return elements


def create_service_section(report_data):
    """Create service type breakdown section."""
    elements = []

    elements.append(
        Paragraph("<b>SERVICE TYPE BREAKDOWN</b>", getSampleStyleSheet()["Heading2"])
    )
    elements.append(Spacer(1, 0.1 * inch))

    service_data = [["Service Type", "Orders", "Amount", "Percentage"]]

    total_amount = report_data["invoices"]["total_revenue"]

    for service, amount in report_data["invoices"]["service_breakdown"][
        "amounts"
    ].items():
        count = report_data["invoices"]["service_breakdown"]["counts"].get(service, 0)
        percentage = (amount / total_amount * 100) if total_amount > 0 else 0
        service_data.append(
            [service, f"{count:,}", f"{amount:,.2f}", f"{percentage:.1f}%"]
        )

    service_table = Table(
        service_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch, 1 * inch]
    )
    service_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a4a4a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    elements.append(service_table)
    elements.append(Spacer(1, 0.3 * inch))

    return elements


def create_top_items_section(report_data):
    """Create top selling items section."""
    elements = []

    elements.append(
        Paragraph(
            f"<b>TOP {config.TOP_ITEMS_COUNT} SELLING ITEMS</b>",
            getSampleStyleSheet()["Heading2"],
        )
    )
    elements.append(Spacer(1, 0.1 * inch))

    items_data = [["Rank", "Item", "Qty Sold", "Revenue", "Profit"]]

    for i, item in enumerate(report_data["sales"]["top_items"], 1):
        items_data.append(
            [
                str(i),
                item["ITEMS"],
                f"{int(item['QTY']):,}",
                f"{item['AMOUNT']:,.2f}",
                f"{item['PROFIT']:,.2f}",
            ]
        )

    items_table = Table(
        items_data, colWidths=[0.5 * inch, 2.5 * inch, 1 * inch, 1.5 * inch, 1.5 * inch]
    )
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a4a4a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (1, 0), (1, -1), "LEFT"),
                ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.beige, colors.white]),
            ]
        )
    )

    elements.append(items_table)
    elements.append(Spacer(1, 0.3 * inch))

    return elements


def create_category_section(report_data):
    """Create category performance section."""
    elements = []

    elements.append(
        Paragraph("<b>CATEGORY PERFORMANCE</b>", getSampleStyleSheet()["Heading2"])
    )
    elements.append(Spacer(1, 0.1 * inch))

    category_data = [["Category", "Items Sold", "Revenue", "Profit", "Margin %"]]

    for cat in report_data["sales"]["category_performance"]:
        margin = (cat["PROFIT"] / cat["AMOUNT"] * 100) if cat["AMOUNT"] > 0 else 0
        category_data.append(
            [
                cat["CATOGERY"],
                f"{int(cat['QTY']):,}",
                f"{cat['AMOUNT']:,.2f}",
                f"{cat['PROFIT']:,.2f}",
                f"{margin:.1f}%",
            ]
        )

    category_table = Table(
        category_data,
        colWidths=[2 * inch, 1.2 * inch, 1.5 * inch, 1.5 * inch, 1 * inch],
    )
    category_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a4a4a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.beige, colors.white]),
            ]
        )
    )

    elements.append(category_table)
    elements.append(Spacer(1, 0.3 * inch))

    return elements


def create_footer(canvas, doc):
    """Add footer to each page."""
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.drawString(
        inch, 0.75 * inch, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    canvas.drawRightString(letter[0] - inch, 0.75 * inch, f"Page {doc.page}")
    canvas.restoreState()


def generate_pdf(report_data, output_path=None):
    """
    Generate PDF report from analyzed data.

    Args:
        report_data: Dict with analyzed metrics
        output_path: Optional file path. If None, returns BytesIO

    Returns:
        BytesIO object if output_path is None, otherwise None
    """
    # Create PDF
    if output_path:
        pdf = SimpleDocTemplate(output_path, pagesize=letter)
    else:
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)

    # Container for elements
    elements = []
    styles = getSampleStyleSheet()

    # Build report sections
    elements.extend(create_header(styles, report_data))
    elements.extend(create_summary_section(report_data))
    elements.extend(create_payment_section(report_data))
    elements.extend(create_service_section(report_data))
    elements.extend(create_top_items_section(report_data))
    elements.extend(create_category_section(report_data))

    # Build PDF
    pdf.build(elements, onFirstPage=create_footer, onLaterPages=create_footer)

    if output_path:
        print(f"PDF generated: {output_path}")
        return None
    else:
        buffer.seek(0)
        return buffer


if __name__ == "__main__":
    # Test PDF generation
    from extract import get_monthly_data
    from analyze import generate_report_data

    data = get_monthly_data(2025, 11)
    report = generate_report_data(data["invoices"], data["sales"])

    generate_pdf(report, "test_October-report.pdf")
    print("Test PDF created: test_report.pdf")
