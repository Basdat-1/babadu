from django.urls import path
from authentication.views import *

app_name = 'authentication'

urlpatterns = [
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('register-atlet/', register_atlet, name='register-atlet'),
    path('logout/', logout, name='logout')
]