from django.urls import path
from . import views
from .quickbooks import views as qb_views

app_name = 'admin_tools'

urlpatterns = [
    # Admin Dashboard
    path('', views.home, name='home'),
    
    # User Management
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    
    # System
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('settings/', views.system_settings, name='system_settings'),
    
    # QuickBooks Integration
    path('quickbooks/', qb_views.dashboard, name='quickbooks_dashboard'),
    path('quickbooks/settings/', qb_views.settings, name='quickbooks_settings'),
    path('quickbooks/sync/', qb_views.sync_dashboard, name='quickbooks_sync_dashboard'),
    path('quickbooks/sync/history/', qb_views.sync_history, name='quickbooks_sync_history'),
    path('quickbooks/sync/progress/', qb_views.sync_progress, name='quickbooks_sync_progress'),
]
