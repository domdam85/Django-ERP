from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def percentage(value, total):
    try:
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def count_by_status(items, status):
    return items.filter(status=status).count()

@register.filter
def sum_quantities(items):
    """Sum the total_quantity field for all items"""
    return sum(item.total_quantity for item in items)

@register.filter
def sum_picked_quantities(items):
    """Sum the picked_quantity field for all items, treating None as 0"""
    return sum(item.picked_quantity or 0 for item in items)
