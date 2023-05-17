from django.urls import path
from authentication.views import index

app_name = 'authentication'

urlpatterns = [
    path('', index, name='index'),
]