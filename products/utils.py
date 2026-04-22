from PIL import Image
from decimal import Decimal

def resize_image(image_path, size=(800, 800)):
    img = Image.open(image_path)
    img = img.convert("RGB")
    img = img.resize(size)
    img.save(image_path, optimize=True, quality=85)  

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