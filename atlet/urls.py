from django.urls import path
from atlet.views import atletHome, daftarStadium, daftarEventStadium, daftarPartaiKompetisi

app_name = 'atlet'

urlpatterns = [
    path('', atletHome, name='home'),
    path('daftar-event/stadium', daftarStadium, name='daftar_stadium'),
    path('daftar-event/stadium/<str:namaStadium>', daftarEventStadium, name='daftar-event-stadium'),
    path('daftar-event/stadium/<str:namaStadium>/<str:namaEvent>/<str:tahunEvent>', daftarPartaiKompetisi, name='daftar-partai-kompetisi'),

]