from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import InventoryForm

# Create your views here.

@login_required
def home(request):
    context = {
        'page_title': 'Warehouse Dashboard'
    }
    return render(request, 'warehouse/home.html', context)

@login_required
def inventory_list(request):
    return render(request, 'warehouse/inventory_list.html')

@login_required
def inventory_add(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inventory item added successfully.')
            return redirect('warehouse:inventory_list')
    else:
        form = InventoryForm()
    
    context = {
        'form': form,
        'page_title': 'Add Inventory Item'
    }
    return render(request, 'warehouse/inventory_form.html', context)

@login_required
def inventory_detail(request, pk):
    return render(request, 'warehouse/inventory_detail.html')

@login_required
def inventory_adjust(request, pk):
    return render(request, 'warehouse/inventory_adjust.html')

@login_required
def picking_list(request):
    return render(request, 'warehouse/picking_list.html')

@login_required
def packing_list(request):
    return render(request, 'warehouse/packing_list.html')

@login_required
def inventory_stats(request):
    total_inventory = 10000
    inventory_data = [
        {'category': 'Raw Materials', 'quantity': 3000},
        {'category': 'Work in Progress', 'quantity': 2000},
        {'category': 'Finished Goods', 'quantity': 5000}
    ]
    
    # Pre-calculate percentages
    for item in inventory_data:
        item['percentage'] = (item['quantity'] / total_inventory) * 100
    
    context = {
        'page_title': 'Inventory Statistics',
        'total_inventory': total_inventory,
        'inventory_data': inventory_data
    }
    return render(request, 'warehouse/inventory_stats.html', context)
