from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    # Overview Section
    path('', views.home, name='home'),
    path('analytics/', views.analytics, name='analytics'),
    
    # Financial Section
    path('revenue/', views.revenue, name='revenue'),
    path('expenses/', views.expenses, name='expenses'),
    path('projections/', views.projections, name='projections'),
    
    # Team Section
    path('team/performance/', views.team_performance, name='team_performance'),
    path('team/schedules/', views.schedules, name='schedules'),
    
    # Reports Section
    path('reports/', views.reports, name='reports'),
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/delivery/', views.delivery_report, name='delivery_report'),
    path('reports/inventory/', views.inventory_report, name='inventory_report'),
    
    # Settings Section
    path('settings/company/', views.company_settings, name='company_settings'),
    path('settings/users/', views.user_management, name='user_management'),
]
