from django.urls import path
from atlet.views import atletHome, daftarStadium, daftarEventStadium, c_sponsor, list_sponsor, daftarPartaiKompetisi, enrolled_event, enrolled_partai_kompetisi
app_name = 'atlet'

urlpatterns = [
    path('', atletHome, name='home'),
    path('daftar-event/stadium', daftarStadium, name='daftar_stadium'),
    path('daftar-event/stadium/<str:namaStadium>', daftarEventStadium, name='daftar-event-stadium'),
    path('c-sponsor', c_sponsor, name='c_sponsor'),
    path('list-sponsor/', list_sponsor, name='list_sponsor'),
    path('daftar-event/stadium/<str:namaStadium>/<str:namaEvent>/<str:tahunEvent>', daftarPartaiKompetisi, name='daftar-partai-kompetisi'),
    path('enrolled-event/', enrolled_event, name='enrolled_event'),
    path('enrolled-partai-kompetisi-event/', enrolled_partai_kompetisi, name='enrolled_partai_kompetisi'),

    


]