from django.urls import path
from umpire.views import *
app_name = 'umpire'

urlpatterns = [
    path('', dashboard_umpire, name='dashboard_umpire'),
    path('daftar-atlet/', daftar_atlet, name='daftar_atlet'),
    path('list-partai-kompetisi/', get_partai_kompetisi, name='get_partai_kompetisi'),
    path('hasil-pertandingan', get_hasil_pertandingan, name='get_hasil_pertandingan'),
    # path('live-score/', c_pertandingan, name='c_pertandingan'),
    path('live-score/<str:namaEvent>/<str:jenisPartai>/<str:tahun>/<str:kategori>', c_pertandingan, name='nama_event'),
    path('get_datetime', get_datetime, name='get_datetime'),
    path('save_stopwatch', save_stopwatch, name='save_stopwatch'),
    path('save_match', save_match, name='save_match'),
    path('save_final', save_final, name='save_final'),
    path('update_score/', update_score, name='update_score'),

]

