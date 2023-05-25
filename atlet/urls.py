from django.urls import path
from atlet.views import *

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

    

    path('join/', joinEvent, name='join-event'),
    path('ujian-kualifikasi/pilih', pilih_ujian_kualifikasi, name='pilih_ujian_kualifikasi'),
    path('ujian-kualifikasi/soal', soal_ujian_kualifikasi, name='soal_ujian_kualifikasi'),
    path('ujian-kualifikasi/riwayat', riwayat_ujian_kualifikasi, name='riwayat_ujian_kualifikasi'),

]