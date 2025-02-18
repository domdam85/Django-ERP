from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
from django_tables2 import RequestConfig
from .models import SyncSession, Customer, QuickBooksSettings
from .sync_manager import SyncManager
from .tables import SyncSessionTable
import logging
import threading
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

logger = logging.getLogger(__name__)
sync_manager = SyncManager()

@login_required
def dashboard(request):
    """QuickBooks integration dashboard showing overall status"""
    settings = QuickBooksSettings.objects.first()
    sync_stats = {
        'total': Customer.objects.count(),
        'synced': Customer.objects.filter(sync_status='synced').count(),
        'pending': Customer.objects.filter(sync_status='pending').count(),
        'error': Customer.objects.filter(sync_status='error').count(),
    }
    
    return render(request, 'admin_tools/quickbooks/dashboard.html', {
        'settings': settings,
        'sync_stats': sync_stats,
    })

@login_required
def settings(request):
    """QuickBooks configuration settings"""
    settings = QuickBooksSettings.objects.first()
    
    if request.method == 'POST' and 'save_settings' in request.POST:
        # Handle settings update
        api_key = request.POST.get('conductor_api_key')
        end_user_id = request.POST.get('conductor_end_user_id')
        sync_enabled = request.POST.get('sync_enabled') == 'on'
        
        if not settings:
            settings = QuickBooksSettings()
        
        settings.conductor_api_key = api_key
        settings.conductor_end_user_id = end_user_id
        settings.sync_enabled = sync_enabled
        settings.save()
    
    return render(request, 'admin_tools/quickbooks/settings.html', {
        'settings': settings,
    })

@login_required
def sync_dashboard(request):
    """QuickBooks sync dashboard view"""
    if request.method == 'POST':
        action = request.POST.get('action')
        logger.info(f"Received sync action: {action}")
        
        if action == 'start_sync':
            # First check if a sync is already running
            current_session = SyncSession.objects.filter(status='running').first()
            if current_session:
                return JsonResponse({
                    'status': 'error',
                    'message': "A sync is already in progress"
                })
            
            # Start sync in background thread
            sync_objects = request.POST.getlist('sync_objects')
            logger.info(f"Starting sync for objects: {sync_objects}")
            
            if not sync_objects:
                return JsonResponse({
                    'status': 'error',
                    'message': "No objects selected for sync"
                })
            
            # Create new sync session
            session = SyncSession.objects.create(
                status='running',
                total_objects=Customer.objects.count(),
                start_time=timezone.now()
            )
            
            def run_sync():
                try:
                    sync_manager.start_sync(sync_objects)
                except Exception as e:
                    logger.error(f"Error in sync thread: {str(e)}")
                    session.refresh_from_db()
                    if session.status == 'running':  # Only update if not cancelled
                        session.status = 'failed'
                        session.end_time = timezone.now()
                        session.save()
            
            thread = threading.Thread(target=run_sync)
            thread.daemon = True
            thread.start()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Sync started'
            })
            
        elif action == 'cancel_sync':
            # Cancel any running syncs
            current_session = SyncSession.objects.filter(status='running').first()
            if current_session:
                current_session.status = 'cancelled'
                current_session.end_time = timezone.now()
                current_session.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Sync cancelled'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No sync in progress'
                })
            
        return JsonResponse({
            'status': 'error',
            'message': "Invalid action"
        })
    
    # Get sync stats
    customer_stats = {
        'total': Customer.objects.count(),
        'synced': Customer.objects.filter(sync_status='synced').count(),
        'pending': Customer.objects.filter(sync_status='pending').count()
    }
    
    # Get current session
    current_session = SyncSession.objects.filter(status='running').first()
    
    return render(request, 'admin_tools/quickbooks/sync_dashboard.html', {
        'customer_sync_enabled': True,
        'customer_stats': customer_stats,
        'current_session': current_session
    })

@login_required
def sync_progress(request):
    """HTMX endpoint for sync progress updates"""
    current_session = SyncSession.objects.filter(status='running').first()
    
    # Clean up stale sessions (running for more than 1 hour)
    stale_sessions = SyncSession.objects.filter(
        status='running',
        start_time__lt=timezone.now() - timezone.timedelta(hours=1)
    )
    if stale_sessions.exists():
        stale_sessions.update(
            status='failed',
            end_time=timezone.now()
        )
        current_session = None
    
    if current_session:
        # Calculate progress
        customer_total = Customer.objects.count()
        customer_synced = Customer.objects.filter(sync_status='synced').count()
        
        # Update session progress
        current_session.synced_objects = customer_synced
        current_session.total_objects = customer_total
        current_session.progress_percentage = int((customer_synced / max(customer_total, 1)) * 100)
        current_session.save()
    
    return render(request, 'admin_tools/quickbooks/sync_progress.html', {
        'current_session': current_session
    })

@login_required
def sync_history(request):
    """View sync history"""
    table = SyncSessionTable(SyncSession.objects.all().order_by('-start_time'))
    RequestConfig(request).configure(table)
    return render(request, 'admin_tools/quickbooks/sync_history.html', {
        'table': table
    })

@login_required
@require_http_methods(["GET"])
def sync_progress_old(request):
    """HTMX endpoint for sync progress updates"""
    current_session = SyncSession.objects.filter(
        status='running'
    ).first() or SyncSession.objects.first()
    
    if current_session:
        # Calculate object-specific progress
        object_progress_list = []
        object_stats = []
        
        # Add customer progress if applicable
        if current_session.status == 'running':
            customer_progress = {
                'name': 'Customers',
                'color': 'bg-primary',
                'percentage': int((Customer.objects.filter(sync_status='synced').count() / 
                                 max(Customer.objects.count(), 1)) * 100),
                'icon': 'fas fa-users',
                'processed': Customer.objects.filter(sync_status='synced').count(),
                'pending': Customer.objects.filter(sync_status='pending').count(),
                'failed': Customer.objects.filter(sync_status='error').count(),
            }
            object_progress_list.append(customer_progress)
            object_stats.append(customer_progress)
    
    # Check if this is an HTMX request
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'admin_tools/quickbooks/sync_progress.html', {
            'current_session': current_session,
            'object_progress_list': object_progress_list,
            'object_stats': object_stats,
        })
    else:
        # Regular AJAX request - return JSON
        return JsonResponse({
            'current_session': {
                'status': current_session.status if current_session else None,
                'progress': current_session.progress_percentage if current_session else 0,
                'synced_objects': current_session.synced_objects if current_session else 0,
                'failed_objects': current_session.failed_objects if current_session else 0,
                'total_objects': current_session.total_objects if current_session else 0,
            } if current_session else None,
            'object_stats': object_stats
        })
