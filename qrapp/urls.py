from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='qrapp_index'),
    path('catalog/', views.show_catalog, name='catalog'),
    path('product/<uuid:uuid>/', views.product_detail, name="product_detail"),
]