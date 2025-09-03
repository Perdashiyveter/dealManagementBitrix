from django.shortcuts import render
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from config.settings import YANDEX_API_KEY
import requests


@main_auth(on_cookies=True)
def company_map(request):
    but = request.bitrix_user_token
    companies = but.call_list_method('crm.company.list', {
        'select': ['ID','TITLE']
    })

    addresses = but.call_list_method('crm.address.list', {
        'select': ['ANCHOR_ID', 'ADDRESS_1', 'CITY']
    })

    addresses = {item['ANCHOR_ID']: f"{item['CITY']}, {item['ADDRESS_1']}" for item in addresses}

    for company in companies:
        company['ADDRESS'] = addresses[company['ID']]
        coords = requests.get(f'https://geocode-maps.yandex.ru/v1/?apikey={YANDEX_API_KEY}&geocode={company["ADDRESS"]}&format=json').json()
        coords = coords["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        company['COORDS'] = coords

    return render(request, 'companies/index.html', {'companies': companies, 'YANDEX_API_KEY': YANDEX_API_KEY})
