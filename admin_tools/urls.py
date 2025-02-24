from django.urls import path
from . import views

app_name = 'admin_tools'

urlpatterns = [
    path('', views.home, name='home'),
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('settings/', views.system_settings, name='system_settings'),
    path('settings/quickbooks/', views.quickbooks_settings, name='quickbooks_settings'),
]
