from django.urls import path
from atlet.views import *

app_name = 'atlet'

urlpatterns = [
    path('', atletHome, name='home'),
    path('daftar-event/stadium', daftarStadium, name='daftar_stadium'),
    path('daftar-event/stadium/<str:namaStadium>', daftarEventStadium, name='daftar-event-stadium'),
    path('daftar-event/stadium/<str:namaStadium>/<str:namaEvent>/<str:tahunEvent>', daftarPartaiKompetisi, name='daftar-partai-kompetisi'),
    path('join/', joinEvent, name='join-event'),
    path('ujian-kualifikasi/pilih', pilih_ujian_kualifikasi, name='pilih_ujian_kualifikasi'),
    path('ujian-kualifikasi/soal', soal_ujian_kualifikasi, name='soal_ujian_kualifikasi'),
    path('ujian-kualifikasi/riwayat', riwayat_ujian_kualifikasi, name='riwayat_ujian_kualifikasi'),

]