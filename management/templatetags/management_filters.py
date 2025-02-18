from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)

@register.filter
def percentage(value, total):
    """Calculate percentage"""
    try:
        return int((value / total) * 100)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter
def total_completed_stops(routes):
    """Get total completed stops across all routes"""
    total = 0
    for route in routes:
        if hasattr(route, 'progress'):
            total += route.progress.get('completed_stops', 0)
    return total

@register.filter
def total_in_progress_stops(routes):
    """Get total in-progress stops across all routes"""
    total = 0
    for route in routes:
        if hasattr(route, 'progress'):
            total += route.progress.get('in_progress_stops', 0)
    return total

@register.filter
def total_remaining_stops(routes):
    """Get total remaining stops across all routes"""
    total = 0
    for route in routes:
        if hasattr(route, 'progress'):
            progress = route.progress
            total += (progress.get('total_stops', 0) - 
                     progress.get('completed_stops', 0) - 
                     progress.get('in_progress_stops', 0))
    return total

@register.filter
def route_coordinates(stops):
    """Convert stops to coordinates array for Google Maps"""
    coordinates = []
    for stop in stops:
        if hasattr(stop, 'customer') and stop.customer:
            coordinates.append({
                'lat': float(stop.customer.latitude),
                'lng': float(stop.customer.longitude)
            })
    return mark_safe(json.dumps(coordinates))

@register.filter
def avg_stops(routes):
    """Calculate average number of stops per route"""
    if not routes:
        return 0
    total_stops = sum(route.stops.count() for route in routes)
    return round(total_stops / len(routes), 1)

@register.filter
def avg_delivery_time(routes):
    """Calculate average delivery time across all routes"""
    total_time = 0
    count = 0
    for route in routes:
        if hasattr(route, 'metrics'):
            time = route.metrics.get('avg_delivery_time')
            if time:
                total_time += time
                count += 1
    if count == 0:
        return "N/A"
    return f"{round(total_time / count, 1)} min"

@register.filter
def load_balance_score(routes):
    """Calculate load balance score across routes"""
    if not routes:
        return 100
    
    stops = [route.stops.count() for route in routes]
    if not stops:
        return 100
        
    avg = sum(stops) / len(stops)
    max_deviation = max(abs(s - avg) for s in stops)
    max_possible_deviation = avg
    
    if max_possible_deviation == 0:
        return 100
        
    balance_score = 100 * (1 - max_deviation / max_possible_deviation)
    return round(balance_score)
