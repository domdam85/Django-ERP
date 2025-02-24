from django.urls import path
from . import views

app_name = 'warehouse'

urlpatterns = [
    path('', views.home, name='home'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.inventory_add, name='inventory_add'),
    path('inventory/<int:pk>/', views.inventory_detail, name='inventory_detail'),
    path('inventory/<int:pk>/adjust/', views.inventory_adjust, name='inventory_adjust'),
    path('inventory/stats/', views.inventory_stats, name='inventory_stats'),
    path('picking/', views.picking_list, name='picking_list'),
    path('packing/', views.packing_list, name='packing_list'),
]
