from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO


def generate_invoice(order, order_items):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    elements = []

    # Store Header
    elements.append(Paragraph("<b>SMASHSTRIX</b>", styles["Title"]))
    elements.append(Paragraph("Premium Sports Store", styles["Normal"]))
    elements.append(Paragraph("support@smashstrix.com", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Invoice Title
    elements.append(Paragraph("<b>INVOICE</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    # Order Information
    order_info = [
        ["Order ID", order.order_id],
        ["Order Date", order.created_at.strftime("%d %b %Y")],
        ["Payment Method", order.payment_method],
    ]

    order_table = Table(order_info, colWidths=[150, 300])

    order_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.lightgrey),
    ]))

    elements.append(order_table)
    elements.append(Spacer(1, 20))

    # Shipping Address
    elements.append(Paragraph("<b>Shipping Address</b>", styles["Heading3"]))
    elements.append(Paragraph(order.address.full_name, styles["Normal"]))
    elements.append(Paragraph(order.address.address_line, styles["Normal"]))
    elements.append(
        Paragraph(
            f"{order.address.city}, {order.address.state} - {order.address.pincode}",
            styles["Normal"],
        )
    )
    elements.append(Paragraph(f"Phone : {order.address.phone}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Product Table
    data = [["Product", "Color", "Qty", "Price", "Total"]]

    for item in order_items:

        color = "-"
        if item.color_variant:
            color = item.color_variant.color

        data.append([
            item.product.name,
            color,
            str(item.quantity),
            f"Rs.{item.price}",
            f"Rs.{item.total_price}",
        ])

    product_table = Table(data, colWidths=[200, 80, 50, 80, 80])

    product_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.black),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (2,1), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,1), (-1,-1), colors.whitesmoke),
    ]))

    elements.append(product_table)
    elements.append(Spacer(1, 20))

    # Totals Table
    totals_data = [
        ["Subtotal", f"Rs.{order.subtotal}"],
        ["Tax", f"Rs.{order.tax}"],
        ["Shipping", f"Rs.{order.shipping}"],
    ]
    if order.coupon:
        totals_data.append(["Coupon Applied", order.coupon.code])
    if order.discount and order.discount > 0:
        totals_data.append(["Discount", f"- Rs.{order.discount}"])
    totals_data.append(["Grand Total", f"Rs {order.total}"])
    totals_table = Table(totals_data, colWidths=[350, 100])

    totals_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,-1), (-1,-1), colors.lightgrey),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
    ]))

    elements.append(totals_table)
    elements.append(Spacer(1, 30))

    # Footer
    elements.append(
        Paragraph(
            "Thank you for shopping with SmashStrix!",
            styles["Heading3"]
        )
    )

    elements.append(
        Paragraph(
            "This is a system generated invoice.",
            styles["Normal"]
        )
    )

    doc.build(elements)

    buffer.seek(0)

    return buffer