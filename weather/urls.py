from django.urls import path
from .views import *

app_name = 'blog'

urlpatterns = [
    path('',index,name='index'),
    path('fetch_weather/',fetch_weather,name='fetch_weather'),
    path('get_location/',get_location,name='get_location'),
    path('weather_detail/',weather_detail,name='weather_detail'),
]