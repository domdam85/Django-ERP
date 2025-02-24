from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def home(request):
    context = {
        'page_title': 'Business Overview',
        'today_sales': 0.00,
        'today_orders': 0,
        'pending_deliveries': 0,
        'routes_active': 0,
        'low_stock_count': 0,
        'open_tasks': 0,
        'urgent_tasks': 0,
        'activities': [],
        'tasks': []
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def profile(request):
    return render(request, 'dashboard/profile.html', {'page_title': 'User Profile'})

@login_required
def settings(request):
    return render(request, 'dashboard/settings.html', {'page_title': 'User Settings'})
