from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('', views.home, name='home'),
    path('routes/', views.route_list, name='route_list'),
    path('routes/<int:pk>/', views.route_detail, name='route_detail'),
    path('deliveries/', views.delivery_list, name='delivery_list'),
    path('deliveries/<int:pk>/', views.delivery_detail, name='delivery_detail'),
    path('deliveries/<int:pk>/update/', views.delivery_update, name='delivery_update'),
    path('stats/', views.delivery_stats, name='delivery_stats'),
]
