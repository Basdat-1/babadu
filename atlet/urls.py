from django.urls import path
from atlet.views import atletHome, daftarStadium, daftarEventStadium, c_sponsor, list_sponsor, daftarPartaiKompetisi

app_name = 'atlet'

urlpatterns = [
    path('', atletHome, name='home'),
    path('daftar-event/stadium', daftarStadium, name='daftar_stadium'),
    path('daftar-event/stadium/<str:namaStadium>', daftarEventStadium, name='daftar-event-stadium'),
    path('c-latih-sponsor/', c_sponsor, name='c_sponsor'),
    path('list-sponsor/', list_sponsor, name='list_sponsor'),
    path('daftar-event/stadium/<str:namaStadium>/<str:namaEvent>/<str:tahunEvent>', daftarPartaiKompetisi, name='daftar-partai-kompetisi'),

]