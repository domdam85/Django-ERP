from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from sales.models import Order
from delivery.models import Delivery
from warehouse.models import Product
from .models import PerformanceMetric, Report
from django.contrib import messages

def is_manager(user):
    return user.is_staff

@login_required
@user_passes_test(is_manager, login_url='overview:home')
def home(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access the management section.')
        return redirect('overview:home')
    # Calculate revenue trend
    total_revenue = 0
    revenue_trend = 0
    orders_completed = Order.objects.filter(status='completed').count()
    active_customers = User.objects.filter(is_active=True).count()
    new_customers = User.objects.filter(date_joined__month=request.user.date_joined.month).count()
    
    # Get performance metrics
    fulfillment_rate = 85  # Example value, replace with actual calculation
    delivery_rate = 90     # Example value, replace with actual calculation
    satisfaction_rate = 88 # Example value, replace with actual calculation
    inventory_accuracy = 95 # Example value, replace with actual calculation
    
    # Get recent reports
    recent_reports = Report.objects.all().order_by('-created_at')[:5]
    
    # Example team performance data
    team_performance = [
        {
            'name': 'Sales Team',
            'tasks_completed': 45,
            'total_tasks': 50,
            'completion_rate': 90,
            'performance_rating': 'Excellent',
            'performance_color': 'success'
        },
        {
            'name': 'Delivery Team',
            'tasks_completed': 38,
            'total_tasks': 45,
            'completion_rate': 84,
            'performance_rating': 'Good',
            'performance_color': 'primary'
        }
    ]
    
    # Example revenue chart data
    revenue_chart_data = {
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'datasets': [{
            'label': 'Revenue',
            'data': [65000, 72000, 68000, 75000, 82000, 85000],
            'borderColor': 'rgb(75, 192, 192)',
            'tension': 0.1
        }]
    }
    
    context = {
        'total_revenue': total_revenue,
        'revenue_trend': revenue_trend,
        'orders_completed': orders_completed,
        'active_customers': active_customers,
        'new_customers': new_customers,
        'fulfillment_rate': fulfillment_rate,
        'delivery_rate': delivery_rate,
        'satisfaction_rate': satisfaction_rate,
        'inventory_accuracy': inventory_accuracy,
        'recent_reports': recent_reports,
        'team_performance': team_performance,
        'revenue_chart_data': revenue_chart_data
    }
    
    return render(request, 'management/home.html', context)

@login_required
@user_passes_test(is_manager)
def performance_dashboard(request):
    return render(request, 'management/performance_dashboard.html')

@login_required
@user_passes_test(is_manager)
def route_assignment(request):
    return render(request, 'management/route_assignment.html')

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
    return render(request, 'management/sales_report.html')

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
