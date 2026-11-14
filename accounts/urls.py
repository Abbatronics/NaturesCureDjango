# urls.py
from django.urls import path
from . import views
from .views import send_otp_view, verify_otp_view


urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup-otp/', send_otp_view, name='send_otp'),
    path('verify-otp/', verify_otp_view, name='verify_otp'),

]