from django.urls import path
from umpire.views import dashboard_umpire, daftar_atlet

app_name = 'umpire'

urlpatterns = [
    path('', dashboard_umpire, name='dashboard_umpire'),
    path('daftar_atlet/', daftar_atlet, name='daftar_atlet'),
]