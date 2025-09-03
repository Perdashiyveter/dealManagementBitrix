from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='contacts_index'),
    path('import/', views.import_contacts, name='import_contacts'),
    path('export/', views.export_contacts, name='export_contacts'),
]