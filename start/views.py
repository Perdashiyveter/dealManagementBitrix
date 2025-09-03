from django.shortcuts import render, redirect
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth


# Create your views here.
@main_auth(on_start=True, set_cookie=True)
def start(request):
    return redirect('start_index')


@main_auth(on_cookies=True)
def index(request):
    user = request.bitrix_user
    projects = [
        {'name': 'Приложение 1. Управление сделками', 'url': '/deals/'},
        {'name': 'Приложение 2. Товары и QR-коды', 'url': '/qrapp/'},
        {'name': 'Приложение 3. Таблица сотрудников', 'url': '/employees/'},
        {'name': 'Приложение 4. Вывод компаний на карте', 'url': '/companies/'},
        {'name': 'Приложение 5. Импорт и экспорт контактов', 'url': '/contacts/'},
    ]

    return render(request, "start/index.html", {"projects": projects, "user": user})