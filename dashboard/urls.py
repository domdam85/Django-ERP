from django.urls import path
from . import views

app_name = 'overview'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
]
