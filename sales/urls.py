from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.home, name='home'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_add, name='customer_add'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/add/', views.order_add, name='order_add'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('performance/', views.sales_performance, name='sales_performance'),
]
