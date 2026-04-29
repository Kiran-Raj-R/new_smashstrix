from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from openpyxl import Workbook
from orders.models import Order
from datetime import timedelta
from django.utils import timezone

def get_filtered_orders(request):
    filter_type = request.GET.get("filter", "daily")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    orders = Order.objects.filter(status="delivered")
    today = timezone.now().date()
    if filter_type == "daily":
        orders = orders.filter(created_at__date=today)
    elif filter_type == "weekly":
        orders = orders.filter(created_at__date__gte=today - timedelta(days=7))
    elif filter_type == "monthly":
        orders = orders.filter(created_at__month=today.month)
    elif filter_type == "custom":
        if start_date and end_date:
            orders = orders.filter(created_at__date__range=[start_date, end_date])
    return orders

def generate_sales_pdf(orders):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Sales Report", styles["Title"]))

    data = [["Order ID", "User", "Date", "Total", "Discount"]]

    total_sales = 0
    total_discount = 0

    for order in orders:
        data.append([
            order.order_id,
            order.user.email,
            order.created_at.strftime("%d-%m-%Y"),
            str(order.total),
            str(order.discount)
        ])
        total_sales += order.total
        total_discount += order.discount

    data.append(["", "", "Total", str(total_sales), str(total_discount)])

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)
    return buffer


def generate_sales_excel(orders):

    wb = Workbook()
    ws = wb.active
    ws.title = "Sales Report"

    ws.append(["Order ID", "User", "Date", "Total", "Discount"])

    total_sales = 0
    total_discount = 0

    for order in orders:
        ws.append([
            order.order_id,
            order.user.email,
            order.created_at.strftime("%d-%m-%Y"),
            float(order.total),
            float(order.discount)
        ])
        total_sales += order.total
        total_discount += order.discount

    ws.append(["", "", "Total", float(total_sales), float(total_discount)])

    return wb