from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .quickbooks.models import QuickBooksSettings, Customer
from .quickbooks.sync import CustomerSync

# Create your views here.

@staff_member_required
def home(request):
    return render(request, 'admin_tools/home.html')

@staff_member_required
def user_list(request):
    return render(request, 'admin_tools/user_list.html')

@staff_member_required
def user_add(request):
    return render(request, 'admin_tools/user_form.html')

@staff_member_required
def user_detail(request, pk):
    return render(request, 'admin_tools/user_detail.html')

@staff_member_required
def user_edit(request, pk):
    return render(request, 'admin_tools/user_form.html')

@staff_member_required
def audit_logs(request):
    return render(request, 'admin_tools/audit_logs.html')

@staff_member_required
def system_settings(request):
    return render(request, 'admin_tools/system_settings.html')

@login_required
def quickbooks_settings(request):
    settings = QuickBooksSettings.objects.first()
    customers = Customer.objects.all().order_by('-last_sync_time')[:10]
    sync_stats = {
        'total': Customer.objects.count(),
        'synced': Customer.objects.filter(sync_status='synced').count(),
        'pending': Customer.objects.filter(sync_status='pending').count(),
        'error': Customer.objects.filter(sync_status='error').count(),
    }
    
    if request.method == 'POST':
        if 'save_settings' in request.POST:
            # Save QB settings
            api_key = request.POST.get('conductor_api_key')
            end_user_id = request.POST.get('conductor_end_user_id')
            sync_enabled = request.POST.get('sync_enabled') == 'on'
            
            if settings:
                settings.conductor_api_key = api_key
                settings.conductor_end_user_id = end_user_id
                settings.sync_enabled = sync_enabled
                settings.save()
            else:
                settings = QuickBooksSettings.objects.create(
                    conductor_api_key=api_key,
                    conductor_end_user_id=end_user_id,
                    sync_enabled=sync_enabled
                )
            messages.success(request, 'QuickBooks settings saved successfully.')
            
        elif 'sync_customers' in request.POST:
            try:
                sync = CustomerSync()
                result = sync.sync_customers()
                
                if result['success']:
                    messages.success(
                        request, 
                        f"Successfully synced {result['customers_synced']} customers. "
                        f"{result['customers_failed']} customers failed."
                    )
                else:
                    messages.error(request, f"Sync failed: {result['error']}")
            except Exception as e:
                messages.error(request, f"Error during sync: {str(e)}")
    
    return render(request, 'admin_tools/quickbooks_settings.html', {
        'settings': settings,
        'customers': customers,
        'sync_stats': sync_stats,
    })
