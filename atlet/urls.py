from django.urls import path
from atlet.views import atletHome

app_name = 'atlet'

urlpatterns = [
    path('', atletHome, name='home'),
]