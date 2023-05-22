from django.urls import path
from pelatih.views import dashboard_pelatih, c_latih_atlet, list_atlet

app_name = 'pelatih'

urlpatterns = [
    path('', dashboard_pelatih, name='dashboard_pelatih'),
    path('c-latih-atlet/', c_latih_atlet, name='c_latih_atlet'),
    path('list-atlet/', list_atlet, name='list_atlet'),
]