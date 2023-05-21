from django.urls import path
from atlet.views import atletHome, daftarStadium, daftarEventStadium

app_name = 'atlet'

urlpatterns = [
    path('', atletHome, name='home'),
    path('daftar-event/stadium', daftarStadium, name='daftar-stadium'),
    path('daftar-event/stadium/<str:namaStadium>', daftarEventStadium, name='daftar-event-stadium'),
]