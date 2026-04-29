from PIL import Image
from decimal import Decimal
from django.core.files.base import ContentFile
import io
import os

def resize_image(image_field):

    if not image_field:
        return

    img = Image.open(image_field)
    img = img.convert("RGB")
    img.thumbnail((800, 800))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    file_name = os.path.basename(image_field.name)
    image_field.save(file_name, ContentFile(buffer.getvalue()), save=False)

def get_best_offer(product):
    product_offer = product.offer_percentage or 0
    category_offer = product.category.offer_percentage or 0
    return max(product_offer, category_offer)

def get_best_price(product):
    base_price = product.price
    best_offer = get_best_offer(product)
    if best_offer > 0:
        discount_amount = (base_price * Decimal(best_offer)) / Decimal("100")
        return base_price - discount_amount
    return base_price