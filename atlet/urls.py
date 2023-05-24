from django.urls import path
from atlet.views import atletHome, daftarStadium, daftarEventStadium, c_sponsor, list_sponsor

app_name = 'atlet'

urlpatterns = [
    path('', atletHome, name='home'),
    path('daftar-event/stadium', daftarStadium, name='daftar-stadium'),
    path('daftar-event/stadium/<str:namaStadium>', daftarEventStadium, name='daftar-event-stadium'),
    path('c-latih-sponsor/', c_sponsor, name='c_sponsor'),
    path('list-sponsor/', list_sponsor, name='list_sponsor'),

]