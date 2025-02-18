from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, F, Q
from django.db import transaction
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, DetailView, UpdateView, TemplateView, DeleteView
from django.urls import reverse_lazy

from .models import (
    Product, Vendor, PurchaseOrder, POItem, ReceiptLog, ReceiptItem,
    AggregatedPickList, PickListItem, StagingArea, StagedOrder, Backorder,
    CycleCount, CycleCountItem
)
from .forms import (
    InventoryForm, PurchaseOrderForm, POItemFormSet, ReceiveItemForm,
    PickListForm, StageOrderForm, CycleCountForm
)

# Inventory Views
class InventoryListView(ListView):
    model = Product
    template_name = 'warehouse/inventory/list.html'
    context_object_name = 'inventory_items'

class InventoryCreateView(CreateView):
    model = Product
    template_name = 'warehouse/inventory/form.html'
    form_class = InventoryForm
    success_url = reverse_lazy('warehouse:inventory-list')

class InventoryDetailView(DetailView):
    model = Product
    template_name = 'warehouse/inventory/detail.html'
    context_object_name = 'item'

class InventoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'warehouse/inventory/form.html'
    form_class = InventoryForm
    success_url = reverse_lazy('warehouse:inventory-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Update Inventory Item'
        return context

class InventoryAdjustView(UpdateView):
    model = Product
    template_name = 'warehouse/inventory/form.html'
    form_class = InventoryForm
    success_url = reverse_lazy('warehouse:inventory-list')

class InventoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'warehouse/inventory/confirm_delete.html'
    success_url = reverse_lazy('warehouse:inventory-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Delete Inventory Item'
        return context

class InventoryStatsView(TemplateView):
    template_name = 'warehouse/inventory/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Inventory Statistics'
        return context

# Dashboard View
@login_required
def home(request):
    # Get counts for dashboard
    open_pos = PurchaseOrder.objects.filter(status='open').count()
    pending_picks = AggregatedPickList.objects.filter(
        status='pending',
        delivery_date=timezone.now().date()
    ).count()
    staged_orders = StagedOrder.objects.filter(status='staged').count()
    low_stock = Product.objects.filter(stock_level__lte=F('reorder_point')).count()

    context = {
        'page_title': 'Warehouse Dashboard',
        'open_pos': open_pos,
        'pending_picks': pending_picks,
        'staged_orders': staged_orders,
        'low_stock': low_stock
    }
    return render(request, 'warehouse/home.html', context)

# Purchase Order Views
@login_required
def po_create(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            po = form.save(commit=False)
            po.created_by = request.user
            po.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Purchase Order created successfully.')
            return redirect('warehouse:po-detail', pk=po.pk)
    else:
        form = PurchaseOrderForm()
    
    context = {
        'page_title': 'Create Purchase Order',
        'form': form
    }
    return render(request, 'warehouse/po/form.html', context)

@login_required
def po_list(request):
    purchase_orders = PurchaseOrder.objects.all().order_by('-created_at')
    context = {
        'page_title': 'Purchase Orders',
        'purchase_orders': purchase_orders
    }
    return render(request, 'warehouse/po/list.html', context)

@login_required
def po_detail(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    context = {
        'page_title': f'Purchase Order #{po.id}',
        'po': po
    }
    return render(request, 'warehouse/po/detail.html', context)

@login_required
def po_update(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=po)
        if form.is_valid():
            form.save()
            messages.success(request, 'Purchase Order updated successfully.')
            return redirect('warehouse:po-detail', pk=po.pk)
    else:
        form = PurchaseOrderForm(instance=po)
    
    context = {
        'page_title': f'Update Purchase Order #{po.id}',
        'form': form,
        'po': po
    }
    return render(request, 'warehouse/po/form.html', context)

@login_required
def po_delete(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        po.delete()
        messages.success(request, 'Purchase Order deleted successfully.')
        return redirect('warehouse:po-list')
    
    context = {
        'page_title': f'Delete Purchase Order #{po.id}',
        'po': po
    }
    return render(request, 'warehouse/po/delete.html', context)

@login_required
def po_receive(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        form = ReceiveOrderForm(request.POST)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.purchase_order = po
            receipt.received_by = request.user
            receipt.save()
            form.save_m2m()
            
            # Update PO status if all items received
            if po.is_fully_received():
                po.status = 'received'
                po.save()
            
            messages.success(request, 'Items received successfully.')
            return redirect('warehouse:po-detail', pk=po.pk)
    else:
        form = ReceiveOrderForm()
    
    context = {
        'page_title': f'Receive Items - PO #{po.id}',
        'form': form,
        'po': po
    }
    return render(request, 'warehouse/po/receive.html', context)

@login_required
def po_print(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    context = {
        'page_title': f'Print Purchase Order #{po.id}',
        'po': po
    }
    return render(request, 'warehouse/po/print.html', context)

@login_required
def po_list(request):
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')

    purchase_orders = PurchaseOrder.objects.all()

    if status_filter:
        purchase_orders = purchase_orders.filter(status=status_filter)
    
    if search_query:
        purchase_orders = purchase_orders.filter(
            Q(po_number__icontains=search_query) |
            Q(vendor__name__icontains=search_query)
        )

    context = {
        'purchase_orders': purchase_orders,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'warehouse/po/list.html', context)

@login_required
def po_detail(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    context = {
        'po': po,
        'items': po.items.all().select_related('product'),
        'receipts': po.receipts.all().prefetch_related('items'),
    }
    return render(request, 'warehouse/po/detail.html', context)

@login_required
@transaction.atomic
def receive_items(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    
    if request.method == 'POST':
        form = ReceiveItemForm(request.POST)
        if form.is_valid():
            # Create receipt log
            receipt = ReceiptLog.objects.create(
                purchase_order=po,
                received_by=request.user,
                notes=form.cleaned_data['notes']
            )

            # Process received items
            for item_id, qty in form.cleaned_data['received_items'].items():
                if qty > 0:
                    po_item = POItem.objects.get(id=item_id)
                    ReceiptItem.objects.create(
                        receipt=receipt,
                        po_item=po_item,
                        quantity_received=qty,
                        notes=form.cleaned_data.get(f'notes_{item_id}', '')
                    )

            messages.success(request, 'Items received successfully')
            return redirect('warehouse:po-detail', pk=po.pk)
    else:
        form = ReceiveItemForm(initial={'po': po})

    context = {
        'form': form,
        'po': po,
        'items': po.items.all().select_related('product'),
    }
    return render(request, 'warehouse/receiving/receive.html', context)

@login_required
def scan_item(request):
    """AJAX endpoint for scanning items during receiving"""
    sku = request.GET.get('sku')
    po_id = request.GET.get('po')

    try:
        po = PurchaseOrder.objects.get(id=po_id)
        po_item = po.items.get(product__sku=sku)
        
        return JsonResponse({
            'success': True,
            'item': {
                'id': po_item.id,
                'product_name': po_item.product.name,
                'ordered_quantity': po_item.ordered_quantity,
                'received_quantity': po_item.received_quantity,
                'remaining_quantity': po_item.ordered_quantity - po_item.received_quantity
            }
        })
    except (PurchaseOrder.DoesNotExist, POItem.DoesNotExist):
        return JsonResponse({
            'success': False,
            'error': 'Item not found on this PO'
        })

# Picking & Staging Views
@login_required
def picking_list(request):
    """List all picking lists for the next business day, organized by route."""
    tomorrow = timezone.now().date() + timezone.timedelta(days=1)
    selected_date = request.GET.get('date', tomorrow.strftime('%Y-%m-%d'))

    try:
        delivery_date = timezone.datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        delivery_date = tomorrow

    # Get pick lists grouped by route
    pick_lists = AggregatedPickList.objects.filter(
        delivery_date=delivery_date
    ).select_related(
        'delivery_route',
        'assigned_to'
    ).prefetch_related(
        'items__product',
        'items__sales_orders'
    ).order_by(
        'delivery_route__name'
    )

    # Aggregate stats for each route
    route_stats = {}
    for pick_list in pick_lists:
        if pick_list.delivery_route_id not in route_stats:
            route_stats[pick_list.delivery_route_id] = {
                'total_orders': 0,
                'total_items': 0,
                'completed_items': 0,
                'route_name': pick_list.delivery_route.name
            }
        
        stats = route_stats[pick_list.delivery_route_id]
        stats['total_orders'] += pick_list.items.count()
        for item in pick_list.items.all():
            stats['total_items'] += item.total_quantity
            stats['completed_items'] += item.picked_quantity or 0

    context = {
        'pick_lists': pick_lists,
        'route_stats': route_stats,
        'delivery_date': delivery_date,
        'selected_date': selected_date,
    }
    return render(request, 'warehouse/picking/list.html', context)

@login_required
@transaction.atomic
def create_pick_list(request):
    """Create a new aggregated pick list for a delivery route."""
    if request.method == 'POST':
        form = PickListForm(request.POST)
        if form.is_valid():
            pick_list = form.save(commit=False)
            pick_list.created_by = request.user
            pick_list.save()
            
            # Create pick list items by aggregating orders
            orders = pick_list.delivery_route.orders.filter(
                delivery_date=pick_list.delivery_date,
                status='confirmed'
            )
            
            # Aggregate quantities by product
            product_totals = {}
            for order in orders:
                for item in order.items.all():
                    if item.product_id not in product_totals:
                        product_totals[item.product_id] = {
                            'total_quantity': 0,
                            'orders': set()
                        }
                    product_totals[item.product_id]['total_quantity'] += item.quantity
                    product_totals[item.product_id]['orders'].add(order)

            # Create pick list items
            for product_id, data in product_totals.items():
                item = PickListItem.objects.create(
                    pick_list=pick_list,
                    product_id=product_id,
                    total_quantity=data['total_quantity']
                )
                item.sales_orders.set(data['orders'])

            messages.success(request, 'Pick list created successfully')
            return redirect('warehouse:pick-list-detail', pk=pick_list.pk)
    else:
        form = PickListForm()

    context = {
        'form': form,
    }
    return render(request, 'warehouse/picking/create.html', context)

@login_required
def pick_list_detail(request, pk):
    """View pick list details and enter picked quantities."""
    pick_list = get_object_or_404(AggregatedPickList, pk=pk)
    items = pick_list.items.all().select_related('product')

    if request.method == 'POST':
        form = PickItemForm(request.POST)
        if form.is_valid():
            item_id = request.POST.get('item_id')
            item = get_object_or_404(PickListItem, id=item_id, pick_list=pick_list)
            
            item.picked_quantity = form.cleaned_data['quantity']
            item.notes = form.cleaned_data['notes']
            item.update_status()
            item.save()

            messages.success(request, f'Updated quantity for {item.product.name}')
            return redirect('warehouse:pick-list-detail', pk=pk)
    else:
        form = PickItemForm()

    context = {
        'pick_list': pick_list,
        'items': items,
        'form': form,
    }
    return render(request, 'warehouse/picking/detail.html', context)

@login_required
def start_picking(request, pk):
    """Mark a pick list as in progress."""
    pick_list = get_object_or_404(AggregatedPickList, pk=pk)
    pick_list.start_picking()
    messages.success(request, 'Started picking process')
    return redirect('warehouse:pick-list-detail', pk=pk)

@login_required
def complete_picking(request, pk):
    """Mark a pick list as completed."""
    pick_list = get_object_or_404(AggregatedPickList, pk=pk)
    pick_list.complete_picking()
    messages.success(request, 'Completed picking process')
    return redirect('warehouse:pick-list-detail', pk=pk)

@login_required
@transaction.atomic
def stage_order(request, pk):
    """Assign a staging area to a completed pick list."""
    pick_list = get_object_or_404(AggregatedPickList, pk=pk, status='completed')
    
    if request.method == 'POST':
        form = StageOrderForm(request.POST)
        if form.is_valid():
            staged_order = form.save(commit=False)
            staged_order.picking_list = pick_list
            staged_order.save()
            
            messages.success(request, 'Order staged successfully')
            return redirect('warehouse:picking-list')
    else:
        form = StageOrderForm()

    context = {
        'form': form,
        'pick_list': pick_list,
    }
    return render(request, 'warehouse/staging/assign.html', context)

# Staging Area Management
@login_required
def staging_areas(request):
    """List all staging areas."""
    areas = StagingArea.objects.all()
    return render(request, 'warehouse/staging/list.html', {'areas': areas})

@login_required
def create_staging_area(request):
    """Create a new staging area."""
    if request.method == 'POST':
        form = StageAreaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staging area created successfully')
            return redirect('warehouse:staging-areas')
    else:
        form = StageAreaForm()

    return render(request, 'warehouse/staging/form.html', {'form': form})

@login_required
def edit_staging_area(request, pk):
    """Edit an existing staging area."""
    area = get_object_or_404(StagingArea, pk=pk)
    if request.method == 'POST':
        form = StageAreaForm(request.POST, instance=area)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staging area updated successfully')
            return redirect('warehouse:staging-areas')
    else:
        form = StageAreaForm(instance=area)

    return render(request, 'warehouse/staging/form.html', {'form': form})

@login_required
def delete_staging_area(request, pk):
    """Delete a staging area."""
    area = get_object_or_404(StagingArea, pk=pk)
    if request.method == 'POST':
        area.delete()
        messages.success(request, 'Staging area deleted successfully')
        return redirect('warehouse:staging-areas')
    return render(request, 'warehouse/staging/confirm_delete.html', {'area': area})

# Cycle Count Views
class CycleCountListView(LoginRequiredMixin, ListView):
    model = CycleCount
    template_name = 'warehouse/cycle_count/list.html'
    context_object_name = 'cycle_counts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Cycle Counts'
        return context

class CycleCountDetailView(LoginRequiredMixin, DetailView):
    model = CycleCount
    template_name = 'warehouse/cycle_count/detail.html'
    context_object_name = 'cycle_count'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Cycle Count #{self.object.id}'
        return context

class CycleCountCreateView(LoginRequiredMixin, CreateView):
    model = CycleCount
    template_name = 'warehouse/cycle_count/form.html'
    form_class = CycleCountForm
    success_url = reverse_lazy('warehouse:cycle-count-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Cycle Count'
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'pending'
        return super().form_valid(form)

class CycleCountUpdateView(LoginRequiredMixin, UpdateView):
    model = CycleCount
    template_name = 'warehouse/cycle_count/form.html'
    form_class = CycleCountForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Update Cycle Count #{self.object.id}'
        return context

    def get_success_url(self):
        return reverse_lazy('warehouse:cycle-count-detail', kwargs={'pk': self.object.pk})

@login_required
def cycle_count_start(request, pk):
    cycle_count = get_object_or_404(CycleCount, pk=pk)
    if cycle_count.status == 'pending':
        cycle_count.status = 'in_progress'
        cycle_count.started_at = timezone.now()
        cycle_count.started_by = request.user
        cycle_count.save()
        messages.success(request, 'Cycle count started successfully.')
    return redirect('warehouse:cycle-count-detail', pk=pk)

@login_required
def cycle_count_complete(request, pk):
    cycle_count = get_object_or_404(CycleCount, pk=pk)
    if cycle_count.status == 'in_progress':
        cycle_count.status = 'completed'
        cycle_count.completed_at = timezone.now()
        cycle_count.completed_by = request.user
        cycle_count.save()

        # Process discrepancies
        for item in cycle_count.items.all():
            if item.counted_quantity != item.expected_quantity:
                Discrepancy.objects.create(
                    cycle_count=cycle_count,
                    product=item.product,
                    expected_quantity=item.expected_quantity,
                    actual_quantity=item.counted_quantity,
                    notes=f'Discrepancy found during cycle count #{cycle_count.id}'
                )

        messages.success(request, 'Cycle count completed successfully.')
    return redirect('warehouse:cycle-count-detail', pk=pk)

@login_required
def cycle_count_cancel(request, pk):
    cycle_count = get_object_or_404(CycleCount, pk=pk)
    if cycle_count.status in ['pending', 'in_progress']:
        cycle_count.status = 'cancelled'
        cycle_count.save()
        messages.success(request, 'Cycle count cancelled successfully.')
    return redirect('warehouse:cycle-count-list')

@login_required
def cycle_count_item_update(request, pk, item_pk):
    cycle_count = get_object_or_404(CycleCount, pk=pk)
    item = get_object_or_404(CycleCountItem, pk=item_pk, cycle_count=cycle_count)
    
    if request.method == 'POST':
        form = CycleCountItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Count updated successfully.')
            return redirect('warehouse:cycle-count-detail', pk=pk)
    else:
        form = CycleCountItemForm(instance=item)
    
    context = {
        'page_title': f'Update Count - {item.product.name}',
        'form': form,
        'cycle_count': cycle_count,
        'item': item
    }
    return render(request, 'warehouse/cycle_count/item_form.html', context)

@login_required
def cycle_count_report(request, pk):
    cycle_count = get_object_or_404(CycleCount, pk=pk)
    context = {
        'page_title': f'Cycle Count Report #{cycle_count.id}',
        'cycle_count': cycle_count
    }
    return render(request, 'warehouse/cycle_count/report.html', context)

@login_required
def inventory_search(request):
    query = request.GET.get('term', '')
    items = Product.objects.filter(
        Q(sku__icontains=query) | Q(name__icontains=query)
    )[:10]  # Limit to 10 results
    results = []
    for item in items:
        results.append({
            'id': item.id,
            'label': f'{item.sku} - {item.name}',
            'value': item.sku
        })
    return JsonResponse(results, safe=False)

@login_required
def location_search(request):
    query = request.GET.get('term', '')
    locations = StagingArea.objects.filter(
        name__icontains=query
    )[:10]  # Limit to 10 results
    results = []
    for location in locations:
        results.append({
            'id': location.id,
            'label': location.name,
            'value': location.name
        })
    return JsonResponse(results, safe=False)


# AJAX Endpoints
@login_required
def scan_product(request):
    """AJAX endpoint for scanning products during picking."""
    sku = request.GET.get('sku')
    pick_list_id = request.GET.get('pick_list')

    try:
        pick_list = AggregatedPickList.objects.get(id=pick_list_id)
        item = pick_list.items.get(product__sku=sku)
        
        return JsonResponse({
            'success': True,
            'item': {
                'id': item.id,
                'product_name': item.product.name,
                'total_quantity': item.total_quantity,
                'picked_quantity': item.picked_quantity,
                'remaining_quantity': item.total_quantity - item.picked_quantity
            }
        })
    except (AggregatedPickList.DoesNotExist, PickListItem.DoesNotExist):
        return JsonResponse({
            'success': False,
            'error': 'Product not found on this pick list'
        })

@login_required
def update_pick_quantity(request):
    """AJAX endpoint for updating picked quantities."""
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = request.POST.get('quantity')
        
        try:
            item = PickListItem.objects.get(id=item_id)
            item.picked_quantity = int(quantity)
            item.update_status()
            item.save()
            
            return JsonResponse({
                'success': True,
                'status': item.status
            })
        except (PickListItem.DoesNotExist, ValueError):
            return JsonResponse({
                'success': False,
                'error': 'Invalid request'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})

# Van Loading Views
@login_required
def staged_orders(request):
    """List all orders that have been staged and are ready for loading."""
    orders = StagedOrder.objects.filter(
        status='staged'
    ).select_related(
        'picking_list__delivery_route',
        'staging_area'
    ).prefetch_related(
        'picking_list__items__product'
    ).order_by(
        'picking_list__delivery_route__name'
    )

    context = {
        'orders': orders
    }
    return render(request, 'warehouse/van/staged_orders.html', context)

@login_required
def van_loading(request):
    """Show the van loading dashboard with orders grouped by route."""
    tomorrow = timezone.now().date() + timezone.timedelta(days=1)
    staged_orders = StagedOrder.objects.filter(
        picking_list__delivery_date=tomorrow,
        status='staged'
    ).select_related(
        'picking_list__delivery_route',
        'staging_area'
    ).order_by(
        'picking_list__delivery_route__name'
    )

    # Group orders by route
    routes = {}
    for order in staged_orders:
        route = order.picking_list.delivery_route
        if route.id not in routes:
            routes[route.id] = {
                'route': route,
                'orders': [],
                'total_items': 0,
                'loaded_items': 0
            }
        route_data = routes[route.id]
        route_data['orders'].append(order)
        route_data['total_items'] += order.picking_list.items.count()
        route_data['loaded_items'] += order.picking_list.items.filter(status='loaded').count()

    context = {
        'routes': routes.values(),
        'delivery_date': tomorrow
    }
    return render(request, 'warehouse/van/loading.html', context)

@login_required
def start_loading(request, pk):
    """Start loading orders for a route into a van."""
    staged_order = get_object_or_404(StagedOrder, pk=pk)
    staged_order.status = 'loading'
    staged_order.loading_started_at = timezone.now()
    staged_order.save()
    
    messages.success(request, 'Started loading process')
    return redirect('warehouse:van-loading')

@login_required
def scan_loading(request, pk):
    """Show scanning interface for van loading verification."""
    staged_order = get_object_or_404(StagedOrder, pk=pk, status='loading')
    
    return render(request, 'warehouse/van/scan.html', {
        'order': staged_order
    })

@login_required
def complete_loading(request, pk):
    """Mark a staged order as completely loaded into the van."""
    staged_order = get_object_or_404(StagedOrder, pk=pk)
    staged_order.status = 'loaded'
    staged_order.loading_completed_at = timezone.now()
    staged_order.save()

    # Update pick list items to loaded status
    staged_order.picking_list.items.filter(
        status__in=['completed', 'partial']
    ).update(status='loaded')
    
    messages.success(request, 'Loading completed successfully')
    return redirect('warehouse:van-loading')

@login_required
def update_cycle_count(request):
    """AJAX endpoint for updating cycle count quantities."""
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        counted_quantity = request.POST.get('counted_quantity')
        notes = request.POST.get('notes', '')
        
        try:
            item = CycleCountItem.objects.get(id=item_id)
            item.counted_quantity = int(counted_quantity)
            item.discrepancy_notes = notes
            item.save()
            
            return JsonResponse({
                'success': True,
                'has_discrepancy': item.has_discrepancy
            })
        except (CycleCountItem.DoesNotExist, ValueError):
            return JsonResponse({
                'success': False,
                'error': 'Invalid request'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})
