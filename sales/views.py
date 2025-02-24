from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def home(request):
    context = {
        'page_title': 'Sales Dashboard'
    }
    return render(request, 'sales/home.html', context)

@login_required
def customer_list(request):
    return render(request, 'sales/customer_list.html')

@login_required
def customer_add(request):
    return render(request, 'sales/customer_form.html')

@login_required
def customer_detail(request, pk):
    return render(request, 'sales/customer_detail.html')

@login_required
def order_list(request):
    return render(request, 'sales/order_list.html')

@login_required
def order_add(request):
    return render(request, 'sales/order_form.html')

@login_required
def order_detail(request, pk):
    return render(request, 'sales/order_detail.html')

@login_required
def sales_performance(request):
    total_sales = 150000
    sales_data = [
        {'category': 'Product A', 'amount': 50000},
        {'category': 'Product B', 'amount': 35000},
        {'category': 'Product C', 'amount': 65000}
    ]
    
    # Pre-calculate percentages
    for item in sales_data:
        item['percentage'] = (item['amount'] / total_sales) * 100
    
    context = {
        'page_title': 'Sales Performance',
        'total_sales': total_sales,
        'sales_data': sales_data
    }
    return render(request, 'sales/performance.html', context)
