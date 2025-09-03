from django.urls import path
from . import views

urlpatterns = [
    path('', views.start, name='start'),
    path('menu', views.index, name="start_index"),
]
