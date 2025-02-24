from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def home(request):
    context = {
        'page_title': 'Delivery Dashboard'
    }
    return render(request, 'delivery/home.html', context)

@login_required
def route_list(request):
    return render(request, 'delivery/route_list.html')

@login_required
def route_detail(request, pk):
    return render(request, 'delivery/route_detail.html')

@login_required
def delivery_list(request):
    return render(request, 'delivery/delivery_list.html')

@login_required
def delivery_detail(request, pk):
    return render(request, 'delivery/delivery_detail.html')

@login_required
def delivery_update(request, pk):
    return render(request, 'delivery/delivery_update.html')

@login_required
def delivery_stats(request):
    total_deliveries = 1000
    delivery_data = [
        {'status': 'Completed', 'count': 750},
        {'status': 'In Transit', 'count': 200},
        {'status': 'Delayed', 'count': 50}
    ]
    
    # Pre-calculate percentages
    for item in delivery_data:
        item['percentage'] = (item['count'] / total_deliveries) * 100
    
    context = {
        'page_title': 'Delivery Statistics',
        'total_deliveries': total_deliveries,
        'delivery_data': delivery_data
    }
    return render(request, 'delivery/delivery_stats.html', context)
