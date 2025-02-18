from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    # Home/Dashboard
    path('', views.home, name='home'),
    
    # Route management
    path('routes/', views.RouteListView.as_view(), name='route-list'),
    path('route/<int:pk>/', views.RouteDetailView.as_view(), name='route-detail'),
    path('route-overview/', views.RouteOverviewView.as_view(), name='route-overview'),
    path('stop/<int:pk>/', views.NextStopView.as_view(), name='next-stop'),
    
    # Delivery management
    path('deliveries/', views.DeliveryListView.as_view(), name='delivery-list'),
    path('delivery/<int:pk>/', views.DeliveryDetailView.as_view(), name='delivery-detail'),
    path('delivery/<int:pk>/update/', views.DeliveryUpdateView.as_view(), name='delivery-update'),
    
    # Delivery verification process
    path('delivery/<int:pk>/verify/', views.DeliveryVerificationView.as_view(), name='verify-delivery'),
    path('delivery/<int:pk>/proof/', views.ProofOfDeliveryView.as_view(), name='proof-of-delivery'),
    path('delivery/<int:delivery_pk>/exception/<int:stop_pk>/', views.DeliveryExceptionView.as_view(), name='delivery-exception'),
    
    # Van loading
    path('van-loading/<int:pk>/', views.VanLoadingView.as_view(), name='van-loading'),
]
