from django.urls import path
from authentication.views import *

app_name = 'authentication'

urlpatterns = [
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('register-atlet/', register_atlet, name='register-atlet'),
    path('register-pelatih/', register_pelatih, name='register-pelatih'),
    path('register-umpire/', register_umpire, name='register-umpire'),
    path('logout/', logout, name='logout')
]