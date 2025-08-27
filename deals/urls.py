from django.urls import path
from . import views


urlpatterns = [
    path('', views.last_deals, name='deals_index'),
    path('create/', views.create_deal, name="create_deal"),
]