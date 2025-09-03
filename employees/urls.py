from django.urls import path
from . import views


urlpatterns = [
    path('', views.list_employees, name='employees_index'),
    path('add-call/', views.add_call, name="add_call")
]