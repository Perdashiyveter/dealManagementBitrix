from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('start.urls')),
    path('deals/', include('deals.urls')),
    path('qrapp/', include('qrapp.urls')),
    path('employees/', include('employees.urls')),
    path('companies/', include('companies.urls')),
    path('contacts/', include('contacts.urls'))
]
