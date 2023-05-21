from django.urls import path
from umpire.views import dashboard_umpire, daftar_atlet, get_partai_kompetisi

app_name = 'umpire'

urlpatterns = [
    path('', dashboard_umpire, name='dashboard_umpire'),
    path('daftar-atlet/', daftar_atlet, name='daftar_atlet'),
    path('list-partai-kompetisi/', get_partai_kompetisi, name='get_partai_kompetisi'),
]