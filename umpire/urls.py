from django.urls import path
from umpire.views import dashboard_umpire, daftar_atlet, get_partai_kompetisi, get_hasil_pertandingan

app_name = 'umpire'

urlpatterns = [
    path('', dashboard_umpire, name='dashboard_umpire'),
    path('daftar-atlet/', daftar_atlet, name='daftar_atlet'),
    path('list-partai-kompetisi/', get_partai_kompetisi, name='get_partai_kompetisi'),
    path('hasil-pertandingan/', get_hasil_pertandingan, name='get_hasil_pertandingan'),
]