from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    path('', views.home, name='home'),
    path('performance_dashboard/', views.performance_dashboard, name='performance_dashboard'),
    path('route_assignment/', views.route_assignment, name='route_assignment'),
    path('save_route_changes/', views.save_route_changes, name='save_route_changes'),
    path('optimize_routes/', views.optimize_routes, name='optimize_routes'),
    path('balance_loads/', views.balance_loads, name='balance_loads'),
    path('route_optimization/', views.route_optimization, name='route_optimization'),
    path('route_monitoring/', views.route_monitoring, name='route_monitoring'),
    path('reports/', views.reports, name='reports'),
    path('sales_report/', views.sales_report, name='sales_report'),
    path('inventory_report/', views.inventory_report, name='inventory_report'),
    path('analytics/', views.analytics, name='analytics'),
    path('revenue/', views.revenue, name='revenue'),
    path('expenses/', views.expenses, name='expenses'),
    path('projections/', views.projections, name='projections'),
    path('team_performance/', views.team_performance, name='team_performance'),
    path('schedules/', views.schedules, name='schedules'),
    path('company_settings/', views.company_settings, name='company_settings'),
    path('user_management/', views.user_management, name='user_management'),
    
    # API Endpoints
    path('api/dashboard_metrics/', views.dashboard_metrics_api, name='dashboard_metrics_api'),
    path('api/metrics/detail/<str:metric_type>/', views.metric_detail_api, name='metric_detail_api'),
    path('generate_sales_report/', views.generate_sales_report, name='generate_sales_report'),
]
