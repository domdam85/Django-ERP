from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.db.models import Avg, Sum, Count, Q, F
from django.utils import timezone
from sales.models import Order, Customer
from delivery.models import Delivery
from warehouse.models import Product, VanInventory
from .models import Route, CustomerStop, PerformanceMetric
from math import radians, sin, cos, sqrt, atan2
import numpy as np
from typing import List, Dict, Tuple
from geopy.geocoders import Nominatim

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula.
    """
    R = 6371  # Earth radius in kilometers

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def geocode_address(address):
    """Geocodes an address using Nominatim."""
    geolocator = Nominatim(user_agent="django_erp_system")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None, None

def optimize_route_stops(route: Route) -> List[CustomerStop]:
    """
    Optimizes the order of stops within a given route using a Nearest Neighbor algorithm.
    """
    stops = list(route.stops.select_related('customer').order_by('sequence'))
    if not stops:
        return []

    optimized_stops = []
    current_stop = stops.pop(0)  # Start with the first stop in the existing sequence
    optimized_stops.append(current_stop)

    while stops:
        nearest_stop = min(
            stops,
            key=lambda stop: calculate_distance(
                current_stop.customer.latitude,
                current_stop.customer.longitude,
                stop.customer.latitude,
                stop.customer.longitude
            ) if current_stop.customer.latitude and current_stop.customer.longitude and stop.customer.latitude and stop.customer.longitude else float('inf') # Handle missing coordinates
        )
        optimized_stops.append(nearest_stop)
        stops.remove(nearest_stop)
        current_stop = nearest_stop

    # Update sequence numbers based on optimized order
    for index, stop in enumerate(optimized_stops):
        stop.sequence = index + 1
        stop.save() # Save the updated sequence

    return optimized_stops

def balance_route_loads(routes: List[Route]) -> Dict[int, List[CustomerStop]]:
    """
    Balances the number of stops across routes, ensuring no single route is overloaded.
    This is a basic implementation and can be enhanced with more sophisticated load metrics.
    """
    all_stops = []
    for route in routes:
        all_stops.extend(list(route.customerstop_set.all())) # Changed to use related_name

    avg_stops_per_route = len(all_stops) / len(routes) if routes else 0
    balanced_routes = {route.id: [] for route in routes}
    route_index = 0
    stop_counter = 0

    for stop in all_stops:
        if route_index >= len(routes):
            route_index = 0  # Reset route index if out of routes, distribute remaining stops

        balanced_routes[routes[route_index].id].append(stop)
        stop_counter += 1
        if stop_counter > avg_stops_per_route and route_index < len(routes) -1: # Distribute more evenly
            route_index += 1
            stop_counter = 0 # Reset counter for next route

    # Update sequence numbers and route assignments based on balanced distribution
    for route in routes:
        stops_for_route = balanced_routes[route.id]
        for index, stop in enumerate(stops_for_route):
            stop.sequence = index + 1
            stop.route = route # Ensure stop is assigned to the correct route
            stop.save() # Save route and sequence

    return balanced_routes

def get_daily_metrics():
    """
    Calculates daily operational metrics for the management dashboard.
    """
    today = timezone.now()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)

    total_revenue = Order.objects.filter(
        status='completed',
        created_at__gte=today_start,
        created_at__lte=today_end
    ).aggregate(total_revenue=Sum(F('items__quantity') * F('items__unit_price')))['total_revenue'] or 0

    # Revenue trend (compare today vs yesterday)
    yesterday_start = today_start - timedelta(days=1)
    yesterday_end = today_end - timedelta(days=1)
    yesterday_revenue = Order.objects.filter(
        status='completed',
        created_at__gte=yesterday_start,
        created_at__lte=yesterday_end
    ).aggregate(yesterday_revenue=Sum(F('items__quantity') * F('items__unit_price')))['yesterday_revenue'] or 0

    revenue_trend = ((total_revenue - yesterday_revenue) / yesterday_revenue) * 100 if yesterday_revenue else 100 if total_revenue else 0

    orders_completed = Order.objects.filter(
        status='completed',
        created_at__gte=today_start,
        created_at__lte=today_end
    ).count()

    delivery_total = Delivery.objects.filter(created_at__gte=today_start, created_at__lte=today_end).count()
    delivery_completed = Delivery.objects.filter(
        status='completed',
        created_at__gte=today_start,
        created_at__lte=today_end
    ).count()
    delivery_rate = (delivery_completed / delivery_total) * 100 if delivery_total else 0

    fulfillment_total = Order.objects.filter(created_at__gte=today_start, created_at__lte=today_end).count()
    fulfillment_completed = Order.objects.filter(
        status='completed',
        created_at__gte=today_start,
        created_at__lte=today_end
    ).count()
    fulfillment_rate = (fulfillment_completed / fulfillment_total) * 100 if fulfillment_total else 0

    # Placeholder metrics until features are implemented
    satisfaction_rate = 0
    inventory_accuracy = 0

    return {
        'total_revenue': total_revenue,
        'revenue_trend': revenue_trend,
        'orders_completed': orders_completed,
        'delivery_rate': delivery_rate,
        'fulfillment_rate': fulfillment_rate,
        'satisfaction_rate': satisfaction_rate,
        'inventory_accuracy': inventory_accuracy,
    }

def get_team_performance_metrics():
    """
    Calculates performance metrics for sales and delivery teams.
    """
    today = timezone.now()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)

    sales_team_users = User.objects.filter(groups__name='Sales')
    delivery_team_users = User.objects.filter(groups__name='Delivery')

    sales_tasks_completed = PerformanceMetric.objects.filter(
        user__in=sales_team_users,
        metric_type='sales',
        date=today.date()
    ).aggregate(completed=Count('id'))['completed'] or 0
    sales_total_tasks = sales_team_users.count()

    delivery_tasks_completed = PerformanceMetric.objects.filter(
        user__in=delivery_team_users,
        metric_type='delivery',
        date=today.date()
    ).aggregate(completed=Count('id'))['completed'] or 0
    delivery_total_tasks = delivery_team_users.count()

    sales_completion_rate = (sales_tasks_completed / sales_total_tasks) * 100 if sales_total_tasks else 0
    delivery_completion_rate = (delivery_tasks_completed / delivery_total_tasks) * 100 if delivery_total_tasks else 0

    return {
        'sales_team': {
            'completed': sales_tasks_completed,
            'total': sales_total_tasks,
            'rate': sales_completion_rate
        },
        'delivery_team': {
            'completed': delivery_tasks_completed,
            'total': delivery_total_tasks,
            'rate': delivery_completion_rate
        }
    }

def get_sales_metrics():
    """
    Calculates key sales performance indicators.
    """
    today = timezone.now()
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)

    monthly_sales_performance = Order.objects.filter(
        status='completed',
        created_at__month=today.month,
        created_at__year=today.year
    ).aggregate(total_sales=Sum(F('items__quantity') * F('items__unit_price')))['total_sales'] or 0

    daily_sales_avg = Order.objects.filter(
        status='completed',
        created_at__gte=today - timedelta(days=30), # Last 30 days
        created_at__lte=today_end
    ).dates('created_at', 'day').annotate(daily_sales=Sum(F('items__quantity') * F('items__unit_price'))).aggregate(average_sales=Avg('daily_sales'))['average_sales'] or 0

    top_selling_products = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity', filter=Q(orderitem__order__status='completed'))
    ).order_by('-total_sold')[:5] # Top 5 products

    customer_order_frequency = Customer.objects.annotate(
        order_count=Count('orders')
    ).aggregate(average_frequency=Avg('order_count'))['average_frequency'] or 0

    return {
        'monthly_sales_performance': monthly_sales_performance,
        'daily_sales_avg': daily_sales_avg,
        'top_selling_products': top_selling_products,
        'customer_order_frequency': customer_order_frequency,
    }

def get_inventory_metrics():
    """
    Calculates key inventory management metrics.
    """
    # Updated to use stock_level instead of quantity_on_hand
    total_inventory_value = Product.objects.annotate(
        inventory_value=F('stock_level') * F('unit_price')
    ).aggregate(total_value=Sum('inventory_value'))['total_value'] or 0

    # Updated to use stock_level instead of quantity_on_hand
    low_stock_items_count = Product.objects.filter(stock_level__lt=F('reorder_point')).count()

    # Placeholder metrics until features are implemented
    avg_inventory_turnover_ratio = 3.5
    warehouse_utilization_rate = 75.0

    return {
        'total_inventory_value': total_inventory_value,
        'low_stock_items_count': low_stock_items_count,
        'avg_inventory_turnover_ratio': avg_inventory_turnover_ratio,
        'warehouse_utilization_rate': warehouse_utilization_rate,
    }

def get_performance_rating(completed_tasks, total_tasks):
    """
    Calculates a performance rating based on completed vs total tasks.
    """
    if total_tasks == 0:
        return "N/A"
    completion_rate = (completed_tasks / total_tasks) * 100
    if completion_rate >= 95:
        return "Excellent"
    elif completion_rate >= 80:
        return "Good"
    elif completion_rate >= 60:
        return "Average"
    else:
        return "Needs Improvement"

def get_performance_color(completed_tasks, total_tasks):
    """
    Returns a color code for performance rating.
    """
    if total_tasks == 0:
        return "gray"
    completion_rate = (completed_tasks / total_tasks) * 100
    if completion_rate >= 95:
        return "green"
    elif completion_rate >= 80:
        return "lightgreen"
    elif completion_rate >= 60:
        return "yellow"
    else:
        return "red"
