from PIL import Image
from decimal import Decimal

def resize_image(image_path, size=(800, 800)):
    img = Image.open(image_path)
    img = img.convert("RGB")
    img = img.resize(size)
    img.save(image_path, optimize=True, quality=85)  

def get_best_price(product):
    base_price = product.price
    product_offer = product.offer_percentage or 0
    category_offer = product.category.offer_percentage or 0
    best_offer = max(product_offer, category_offer)
    if best_offer > 0:
        discount_amount = (base_price * Decimal(best_offer)) / Decimal("100")
        final_price = base_price - discount_amount
    else:
        final_price = base_price
    return final_price