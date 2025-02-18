from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Home/Dashboard
    path('', views.home, name='home'),
    
    # Customers
    path('customers/', views.CustomerListView.as_view(), name='customer-list'),
    path('customers/create/', views.CustomerCreateView.as_view(), name='customer-create'),
    path('customer/<int:pk>/', views.CustomerDetailView.as_view(), name='customer-detail'),
    path('customer/<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer-edit'),
    
    # Orders
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('order/<int:pk>/edit/', views.OrderUpdateView.as_view(), name='order-edit'),
    path('customer/<int:customer_pk>/order/new/', views.OrderEntryView.as_view(), name='order-create'),
    
    # Route management
    path('route/', views.RouteOverviewView.as_view(), name='route-overview'),
    path('route/<int:pk>/', views.CustomerStopView.as_view(), name='customer-stop'),
]
