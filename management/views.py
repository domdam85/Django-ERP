from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Avg, Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .utils import (
    get_daily_metrics, get_performance_rating, get_performance_color,
    get_team_performance_metrics, get_sales_metrics, 
    get_inventory_metrics, optimize_route_stops, balance_route_loads
)
from sales.models import Order, Customer
from delivery.models import Delivery
from warehouse.models import Product
from .models import PerformanceMetric, Report, Route, CustomerStop
from django.contrib import messages
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string


def is_manager(user):
    return user.is_staff

@login_required
@user_passes_test(is_manager, login_url='overview:home')
def home(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access the management section.')
        return redirect('overview:home')

    # Get core metrics from utility functions using get_daily_metrics
    metrics = get_daily_metrics()

    # Calculate customer metrics
    today = timezone.now()
    start_of_month = today.replace(day=1)
    active_customers = User.objects.filter(
        is_active=True,
        last_login__gte=today - timezone.timedelta(days=30)
    ).count()
    new_customers = User.objects.filter(
        date_joined__gte=start_of_month
    ).count()

    # Get recent reports
    recent_reports = Report.objects.all().order_by('-created_at')[:5]

    # Get team performance data using get_team_performance_metrics
    team_metrics = get_team_performance_metrics()

    team_performance = [
        {
            'name': 'Sales Team',
            'tasks_completed': team_metrics['sales_team']['completed'],
            'total_tasks': team_metrics['sales_team']['total'],
            'completion_rate': team_metrics['sales_team']['rate'],
            'performance_rating': get_performance_rating(team_metrics['sales_team']['completed'], team_metrics['sales_team']['total']),
            'performance_color': get_performance_color(team_metrics['sales_team']['completed'], team_metrics['sales_team']['total'])
        },
        {
            'name': 'Delivery Team',
            'tasks_completed': team_metrics['delivery_team']['completed'],
            'total_tasks': team_metrics['delivery_team']['total'],
            'completion_rate': team_metrics['delivery_team']['rate'],
            'performance_rating': get_performance_rating(team_metrics['delivery_team']['completed'], team_metrics['delivery_team']['total']),
            'performance_color': get_performance_color(team_metrics['delivery_team']['completed'], team_metrics['delivery_team']['total'])
        }
    ]

    # Get revenue chart data
    last_6_months = []
    revenue_data = []

    for i in range(5, -1, -1):
        month = today.replace(day=1) - timezone.timedelta(days=i*30)
        last_6_months.append(month.strftime('%b'))
        month_revenue = Order.objects.filter(
            created_at__year=month.year,
            created_at__month=month.month,
            status='completed'
        ).aggregate(total=Sum(F('items__quantity') * F('items__unit_price')))[
            'total'
        ] or 0
        revenue_data.append(month_revenue)

    revenue_chart_data = {
        'labels': last_6_months,
        'datasets': [{
            'label': 'Revenue',
            'data': revenue_data,
            'borderColor': 'rgb(75, 192, 192)',
            'tension': 0.1
        }]
    }

    # Get additional metrics using other utility functions
    sales_metrics = get_sales_metrics()
    inventory_metrics = get_inventory_metrics()

    context = {
        'total_revenue': metrics['total_revenue'],
        'revenue_trend': metrics['revenue_trend'],
        'orders_completed': metrics['orders_completed'],
        'active_customers': active_customers,
        'new_customers': new_customers,
        'fulfillment_rate': metrics['fulfillment_rate'],
        'delivery_rate': metrics['delivery_rate'],
        'satisfaction_rate': metrics['satisfaction_rate'],
        'inventory_accuracy': metrics['inventory_accuracy'],
        'recent_reports': recent_reports,
        'team_performance': team_performance,
        'revenue_chart_data': json.dumps(revenue_chart_data), # Serialize to JSON string
        'sales_metrics': sales_metrics,
        'inventory_metrics': inventory_metrics
    }

    return render(request, 'management/home.html', context)

@login_required
@user_passes_test(is_manager)
def performance_dashboard(request):
    return render(request, 'management/performance_dashboard.html')

@login_required
@user_passes_test(is_manager)
def route_assignment(request):
    """
    Route Assignment view with drag-and-drop interface.
    Allows managers to assign customers to routes and routes to sales reps/drivers.
    """
    # Get all routes with their related data
    routes = Route.objects.all().prefetch_related(
        'stops__customer',
        'sales_rep',
        'delivery_driver'
    ).order_by('day', 'name')

    # Get all unassigned customers
    from sales.models import Customer
    unassigned_customers = Customer.objects.exclude(
        id__in=CustomerStop.objects.values_list('customer_id', flat=True)
    )

    # Get available sales reps and drivers
    sales_reps = User.objects.filter(groups__name='Sales')
    drivers = User.objects.filter(groups__name='Delivery')

    # Get route statistics
    from sales.models import Order
    from delivery.models import Delivery

    route_stats = {}
    for route in routes:
        # Calculate statistics for each route
        route_stats[route.id] = {
            'total_stops': route.stops.count(),
            'completed_stops': 0,  # Will be updated below
            'total_orders': 0,
            'completed_deliveries': 0
        }
        
        # Get customer IDs for this route
        customer_ids = route.stops.values_list('customer_id', flat=True)
        
        # Count orders for today for this route's customers
        today_orders = Order.objects.filter(
            customer_id__in=customer_ids,
            created_at__date=timezone.now().date()
        )
        route_stats[route.id]['total_orders'] = today_orders.count()
        
        # Count completed deliveries for today
        completed_deliveries = Delivery.objects.filter(
            order__customer_id__in=customer_ids,
            status='completed',
            created_at__date=timezone.now().date()
        )
        route_stats[route.id]['completed_deliveries'] = completed_deliveries.count()
        
        # Calculate completed stops based on orders and deliveries
        route_stats[route.id]['completed_stops'] = completed_deliveries.values('order__customer').distinct().count()

    context = {
        'routes': routes,
        'unassigned_customers': unassigned_customers,
        'sales_reps': sales_reps,
        'drivers': drivers,
        'route_stats': route_stats,
        'days_of_week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    }
    return render(request, 'management/route_assignment.html', context)


@login_required
@user_passes_test(is_manager)
@csrf_exempt
def save_route_changes(request):
    """
    Endpoint to save route changes via AJAX.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            changes = data.get('changes', [])

            for change in changes:
                if change['action'] == 'add_customer':
                    customer_id = change['customerId']
                    route_id = change['routeId']
                    route = Route.objects.get(id=route_id)
                    
                    # Determine the next sequence number
                    last_stop_in_route = route.stops.last()
                    next_sequence = last_stop_in_route.sequence + 1 if last_stop_in_route else 1
                    
                    CustomerStop.objects.create(
                        customer_id=customer_id,
                        route=route,
                        sequence=next_sequence
                    )

                elif change['action'] == 'reorder_stop':
                    stop_id = change['stopId']
                    route_id = change['routeId']
                    new_position = change['position']
                    
                    stop_to_move = CustomerStop.objects.get(id=stop_id)
                    original_sequence = stop_to_move.sequence
                    
                    if new_position < 0:
                        new_position = 0

                    # Get all stops in the route
                    route_stops = list(CustomerStop.objects.filter(route_id=route_id).order_by('sequence'))
                    
                    if new_position >= len(route_stops):
                        new_position = len(route_stops) - 1 if len(route_stops) > 0 else 0


                    # Remove the stop from the list temporarily
                    route_stops.pop(original_sequence - 1)
                    # Insert the stop at the new position
                    route_stops.insert(new_position, stop_to_move)

                    # Update sequence numbers for all stops in the route
                    for index, stop in enumerate(route_stops):
                        stop.sequence = index + 1
                        stop.save()


                elif change['action'] == 'move_stop':
                    stop_id = change['stopId']
                    source_route_id = change['sourceRouteId']
                    target_route_id = change['targetRouteId']
                    
                    stop_to_move = CustomerStop.objects.get(id=stop_id)
                    source_route = Route.objects.get(id=source_route_id)
                    target_route = Route.objects.get(id=target_route_id)


                    # Determine the next sequence number in the target route
                    last_stop_in_target_route = target_route.stops.last()
                    next_sequence = last_stop_in_target_route.sequence + 1 if last_stop_in_target_route else 1

                    # Update stop to the new route and sequence
                    stop_to_move.route = target_route
                    stop_to_move.sequence = next_sequence
                    stop_to_move.save()

                    # Reorder sequence numbers in the source route
                    source_route_stops = list(CustomerStop.objects.filter(route_id=source_route_id).order_by('sequence'))
                    for index, stop in enumerate(source_route_stops):
                        stop.sequence = index + 1
                        stop.save()


                elif change['action'] == 'update_assignee':
                    route_id = change['routeId']
                    assignee_type = change['assigneeType']
                    assignee_id = change['assigneeId']
                    route = Route.objects.get(id=route_id)
                    
                    if assignee_type == 'sales_rep':
                        route.sales_rep_id = assignee_id or None # Allow unassignment
                    elif assignee_type == 'driver':
                        route.delivery_driver_id = assignee_id or None # Allow unassignment
                    route.save()

            return JsonResponse({'status': 'success', 'message': 'Route changes saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
@user_passes_test(is_manager)
@csrf_exempt
def optimize_routes(request):
    """
    Endpoint to optimize routes via AJAX.
    """
    if request.method == 'POST':
        try:
            routes = Route.objects.all()
            optimized_routes_data = {}

            for route in routes:
                optimized_stops = optimize_route_stops(route)
                optimized_routes_data[route.id] = [
                    {'stop_id': stop.id, 'sequence': stop.sequence, 'customer_name': stop.customer.name}
                    for stop in optimized_stops
                ]

            return JsonResponse({
                'status': 'success',
                'message': 'Routes optimized successfully',
                'optimized_routes': optimized_routes_data
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
@user_passes_test(is_manager)
@csrf_exempt
def balance_loads(request):
    """
    Endpoint to balance route loads via AJAX.
    """
    if request.method == 'POST':
        try:
            print('Balancing route loads - function now implemented')
            routes = Route.objects.all()
            balanced_routes_data = balance_route_loads(routes)
            
            formatted_balanced_routes_data = {}
            for route_id, stops in balanced_routes_data.items():
                formatted_balanced_routes_data[route_id] = [
                    {'stop_id': stop.id, 'sequence': stop.sequence, 'customer_name': stop.customer.customer.name}
                    for stop in stops
                ]

            return JsonResponse({
                'status': 'success',
                'message': 'Route loads balanced successfully',
                'balanced_routes': formatted_balanced_routes_data
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
@user_passes_test(is_manager)
def route_optimization(request):
    """
    Route Optimization view for suggesting optimal route sequences and assignments.
    """
    routes = Route.objects.all().prefetch_related('stops__customer').order_by('day', 'name')
    
    # Get route statistics and performance metrics
    from delivery.models import Delivery
    route_metrics = {}
    
    for route in routes:
        customer_ids = route.stops.values_list('customer_id', flat=True)
        
        # Calculate average delivery times
        deliveries = Delivery.objects.filter(
            order__customer_id__in=customer_ids,
            status='completed'
        )
        
        # Get performance metrics for this route
        metrics = PerformanceMetric.objects.filter(
            metric_type='delivery',
            date=timezone.now().date(),
            user=route.delivery_driver
        ).first()
        
        route_metrics[route.id] = {
            'avg_delivery_time': deliveries.aggregate(Avg('completion_time'))['completion_time__avg'],
            'total_stops': route.stops.count(),
            'performance_score': metrics.value if metrics else None
        }
    
    # Prepare chart data
    route_names = [route.name for route in routes]
    route_scores = [
        route_metrics.get(route.id, {}).get('performance_score', 0) 
        if route_metrics.get(route.id, {}).get('performance_score') is not None 
        else 0 
        for route in routes
    ]
    
    context = {
        'routes': routes,
        'route_metrics': route_metrics,
        'route_names_json': json.dumps(route_names),
        'route_scores_json': json.dumps(route_scores),
        'days_of_week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    }
    return render(request, 'management/route_optimization.html', context)

@login_required
@user_passes_test(is_manager)
def route_monitoring(request):
    """
    Real-time route monitoring dashboard showing current delivery status and progress.
    """
    from delivery.models import Delivery
    from warehouse.models import VanInventory
    import json
    
    # Get all active routes for today
    active_routes = Route.objects.filter(
        status='in_progress',
        delivery_driver__isnull=False
    ).prefetch_related('stops__customer', 'delivery_driver')
    
    route_progress = {}
    route_coordinates = {}
    
    for route in active_routes:
        # Get all deliveries for this route
        customer_ids = route.stops.values_list('customer_id', flat=True)
        deliveries = Delivery.objects.filter(
            order__customer_id__in=customer_ids,
            created_at__date=timezone.now().date()
        )
        
        # Get completed and in-progress stop IDs
        completed_stops = deliveries.filter(status='completed')
        in_progress_stops = deliveries.filter(status='in_progress')
        
        completed_stop_ids = completed_stops.values_list('order__customer_id', flat=True)
        in_progress_stop_ids = in_progress_stops.values_list('order__customer_id', flat=True)
        
        # Get van inventory for this route
        try:
            van_inventory = VanInventory.objects.get(
                driver=route.delivery_driver,
                date=timezone.now().date()
            )
        except VanInventory.DoesNotExist:
            van_inventory = None
            
        route_progress[route.id] = {
            'total_stops': route.stops.count(),
            'completed_stops': completed_stops.count(),
            'completed_stops_ids': list(completed_stop_ids),
            'in_progress_stops': in_progress_stops.count(),
            'in_progress_stops_ids': list(in_progress_stop_ids),
            'remaining_stops': route.stops.count() - (completed_stops.count() + in_progress_stops.count()),
            'van_inventory': van_inventory
        }
        
        # Collect coordinates for each route's stops
        coordinates = []
        for stop in route.stops.all():
            if stop.customer and hasattr(stop.customer, 'latitude') and hasattr(stop.customer, 'longitude'):
                coordinates.append({
                    'lat': float(stop.customer.latitude),
                    'lng': float(stop.customer.longitude)
                })
        route_coordinates[str(route.id)] = coordinates
        
        context = {
            'active_routes': active_routes,
            'route_progress': route_progress,
            'route_coordinates': json.dumps(route_coordinates),
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY  # Make sure to add this to settings.py
        }
        return render(request, 'management/route_monitoring.html', context)

@login_required
@user_passes_test(is_manager)
def reports(request):
    """Main reports dashboard view"""
    context = {
        'page_title': 'Reports Dashboard',
        'report_categories': [
            {
                'name': 'Sales Reports',
                'icon': 'fa-file-invoice-dollar',
                'url': 'management:sales_report',
                'description': 'View detailed sales analytics and trends'
            },
            {
                'name': 'Inventory Reports',
                'icon': 'fa-boxes',
                'url': 'management:inventory_report',
                'description': 'Track inventory levels and stock movement'
            },
            {
                'name': 'Delivery Reports',
                'icon': 'fa-truck',
                'url': 'management:delivery_report',
                'description': 'Monitor delivery performance and logistics'
            }
        ]
    }
    return render(request, 'management/reports.html', context)

@login_required
@user_passes_test(is_manager)
def sales_report(request):
    sales_metrics = get_sales_metrics()
    current_date = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    context = {
        'page_title': 'Sales Report',
        'sales_metrics': sales_metrics,
        'current_date': current_date,
    }
    return render(request, 'management/sales_report.html', context)

@login_required
@user_passes_test(is_manager)
def delivery_report(request):
    return render(request, 'management/delivery_report.html')

@login_required
@user_passes_test(is_manager)
def inventory_report(request):
    return render(request, 'management/inventory_report.html')

@login_required
@user_passes_test(is_manager)
def analytics(request):
    # Add analytics data to context
    context = {
        'page_title': 'Analytics',
        'analytics_data': {
            'daily_sales': [120, 150, 180, 140, 160, 170, 190],
            'weekly_trends': [850, 920, 880, 960, 1020],
            'monthly_growth': 15.5
        }
    }
    return render(request, 'management/analytics.html', context)

@login_required
@user_passes_test(is_manager)
def revenue(request):
    # Add revenue data to context
    context = {
        'page_title': 'Revenue Overview',
        'total_revenue': 150000,
        'monthly_growth': 8.5,
        'revenue_sources': [
            {'name': 'Product Sales', 'amount': 120000},
            {'name': 'Services', 'amount': 25000},
            {'name': 'Subscriptions', 'amount': 5000}
        ]
    }
    return render(request, 'management/revenue.html', context)

@login_required
@user_passes_test(is_manager)
def expenses(request):
    total_expenses = 85000
    expense_categories = [
        {'name': 'Operations', 'amount': 45000},
        {'name': 'Marketing', 'amount': 15000},
        {'name': 'Personnel', 'amount': 25000}
    ]
    
    # Pre-calculate percentages
    for category in expense_categories:
        category['percentage'] = (category['amount'] / total_expenses) * 100
    
    context = {
        'page_title': 'Expenses Overview',
        'total_expenses': total_expenses,
        'expense_categories': expense_categories
    }
    return render(request, 'management/expenses.html', context)

@login_required
@user_passes_test(is_manager)
def projections(request):
    annual_projection = 2000000
    quarterly_targets = [
        {'quarter': 'Q1', 'target': 450000},
        {'quarter': 'Q2', 'target': 500000},
        {'quarter': 'Q3', 'target': 520000},
        {'quarter': 'Q4', 'target': 530000}
    ]
    
    # Pre-calculate percentages
    for quarter in quarterly_targets:
        quarter['percentage'] = (quarter['target'] / annual_projection) * 100
    
    context = {
        'page_title': 'Financial Projections',
        'annual_projection': annual_projection,
        'growth_rate': 12.5,
        'quarterly_targets': quarterly_targets
    }
    return render(request, 'management/projections.html', context)

@login_required
@user_passes_test(is_manager)
def team_performance(request):
    context = {
        'page_title': 'Team Performance',
        'teams': [
            {
                'name': 'Sales Team',
                'performance_score': 92,
                'tasks_completed': 150,
                'goals_met': '95%'
            },
            {
                'name': 'Delivery Team',
                'performance_score': 88,
                'tasks_completed': 200,
                'goals_met': '90%'
            }
        ]
    }
    return render(request, 'management/team_performance.html', context)

@login_required
@user_passes_test(is_manager)
def schedules(request):
    context = {
        'page_title': 'Team Schedules',
        'schedules': [
            {
                'team': 'Sales',
                'shifts': ['Morning', 'Afternoon', 'Evening'],
                'members': 12
            },
            {
                'team': 'Delivery',
                'shifts': ['Morning', 'Afternoon'],
                'members': 8
            }
        ]
    }
    return render(request, 'management/schedules.html', context)

@login_required
@user_passes_test(is_manager)
def company_settings(request):
    context = {
        'page_title': 'Company Settings',
        'company_info': {
            'name': 'ERP System Inc.',
            'address': '123 Business St.',
            'phone': '+1 (555) 123-4567',
            'email': 'contact@erpsystem.com'
        }
    }
    return render(request, 'management/company_settings.html', context)

@login_required
@user_passes_test(is_manager)
def user_management(request):
    users = User.objects.all().order_by('-date_joined')
    context = {
        'page_title': 'User Management',
        'users': users
    }
    return render(request, 'management/user_management.html', context)

@login_required
@user_passes_test(is_manager)
def dashboard_metrics_api(request):
    """API endpoint to get dashboard metrics in JSON format."""
    metrics = get_daily_metrics() # Reuse existing utility function
    
    # Add chart data
    revenue_data = get_revenue_chart_data()
    metrics['revenue_chart_data'] = revenue_data
    
    return JsonResponse(metrics)

@login_required
@user_passes_test(is_manager)
def metric_detail_api(request, metric_type):
    """API endpoint to get detailed information for a specific metric."""
    today = timezone.now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    data = {}
    
    if metric_type == "revenue":
        # Get revenue breakdown by product category
        revenue_by_category = Order.objects.filter(
            created_at__gte=start_of_month,
            status='completed'
        ).values('items__product__category').annotate(
            total=Sum(F('items__quantity') * F('items__unit_price'))
        ).order_by('-total')
        
        # Get top customers by revenue
        top_customers = Order.objects.filter(
            created_at__gte=start_of_month,
            status='completed'
        ).values('customer__name').annotate(
            total=Sum(F('items__quantity') * F('items__unit_price'))
        ).order_by('-total')[:5]
        
        data = {
            'revenue_by_category': list(revenue_by_category),
            'top_customers': list(top_customers),
            'period': 'This Month'
        }
    
    elif metric_type == "orders":
        # Get order statistics
        total_orders = Order.objects.filter(created_at__gte=start_of_month).count()
        completed_orders = Order.objects.filter(
            created_at__gte=start_of_month,
            status='completed'
        ).count()
        
        # Orders by status
        orders_by_status = Order.objects.filter(
            created_at__gte=start_of_month
        ).values('status').annotate(count=Count('id'))
        
        # Average order value
        avg_order_value = Order.objects.filter(
            created_at__gte=start_of_month,
            status='completed'
        ).annotate(
            order_value=Sum(F('items__quantity') * F('items__unit_price'))
        ).aggregate(avg_value=Avg('order_value'))
        
        data = {
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'completion_rate': (completed_orders / total_orders * 100) if total_orders > 0 else 0,
            'orders_by_status': list(orders_by_status),
            'average_order_value': avg_order_value['avg_value'] or 0,
            'period': 'This Month'
        }
    
    elif metric_type == "customers":
        # Active customers
        active_customers = Customer.objects.filter(
            orders__created_at__gte=start_of_month
        ).distinct().count()
        
        # New customers this month
        new_customers = Customer.objects.filter(
            created_at__gte=start_of_month
        ).count()
        
        # Customer order frequency
        customer_frequencies = Customer.objects.annotate(
            order_count=Count('orders', filter=Q(orders__created_at__gte=start_of_month))
        ).aggregate(
            avg_orders=Avg('order_count'),
            max_orders=Max('order_count')
        )
        
        data = {
            'active_customers': active_customers,
            'new_customers': new_customers,
            'average_orders_per_customer': customer_frequencies['avg_orders'] or 0,
            'most_orders_by_customer': customer_frequencies['max_orders'] or 0,
            'period': 'This Month'
        }
    
    elif metric_type == "inventory":
        # Low stock items
        low_stock_items = Product.objects.filter(
            quantity_on_hand__lt=F('reorder_point')
        ).count()
        
        # Stock value by category
        stock_by_category = Product.objects.values('category').annotate(
            value=Sum(F('quantity_on_hand') * F('unit_price'))
        ).order_by('-value')
        
        # Recently updated items
        recent_updates = Product.objects.filter(
            last_updated__gte=today - timedelta(days=7)
        ).values('name', 'quantity_on_hand', 'last_updated')
        
        data = {
            'low_stock_items': low_stock_items,
            'stock_by_category': list(stock_by_category),
            'recent_updates': list(recent_updates),
            'total_items': Product.objects.count()
        }
    
    return JsonResponse(data)

@login_required
@user_passes_test(is_manager)
def generate_sales_report(request):
    """Generates and returns a sales report as HTML."""
    report_data = {
        'report_title': 'Sales Performance Report',
        'sales_metrics': get_sales_metrics(), # Use utility function
        'current_date': timezone.now()
    }
    report_html = render_to_string('management/templates/management/sales_report_template.html', report_data)
    return HttpResponse(report_html, content_type='text/html')
