from django import template
from products.utils import get_best_price  # adjust path if needed

register = template.Library()

@register.filter
def best_price(product):
    return get_best_price(product)