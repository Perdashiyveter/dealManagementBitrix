from django.shortcuts import render, redirect
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from datetime import datetime
from .forms import DealForm


# @main_auth(on_start=True, set_cookie=True)
# def start(request):
#     user = request.bitrix_user
#     print('start')
#     return render(request, 'deals/index.html', {'user': user})


def get_user_deals(but, user_id):
    response = but.call_list_method('crm.deal.list', {
        'order': {
            'BEGINDATE': 'DESC',
            'ID': 'DESC'
        },
        'filter': {
            'ASSIGNED_BY_ID': user_id,
            'CLOSED': 'N'
        },
        'select': ['ID','TITLE','STAGE_ID','OPPORTUNITY','BEGINDATE', 'UF_CRM_1756295581', 'UF_CRM_1756297147'],
        'start': 0
    })

    stage_names = {
        "NEW": "Новая сделка",
        "PREPARATION": "Подготовка документов",
        "PREPAYMENT_INVOICE": "Счёт на предоплату",
        "EXECUTING": "В работе",
        "FINAL_INVOICE": "Финальный счёт"
    }

    payment_methods = {
        None: "—",
        '45': "Наличные",
        '47': "Банковская карта",
        '49': "СБП"
    }

    delivery_methods = {
        None: "—",
        '51': 'Курьер',
        '53': 'Самовывоз',
        '55': 'Пункт выдачи (Яндекс.Маркет, Boxberry)',
        '57': 'Пункт выдачи (CДЭК)',
        '59': 'Почта России'
    }

    deals = []
    for d in response[:10]:
        deals.append({
            'ID': d["ID"],
            'TITLE': d['TITLE'],
            'STAGE': stage_names.get(d["STAGE_ID"], d["STAGE_ID"]),
            'BEGINDATE': datetime.fromisoformat(d.get("BEGINDATE")).strftime("%d.%m.%Y"),
            'OPPORTUNITY': d.get("OPPORTUNITY", "—"),
            'PAYMENT_METHOD': payment_methods.get(d["UF_CRM_1756295581"], d["UF_CRM_1756295581"]),
            'DELIVERY_METHOD': delivery_methods.get(d["UF_CRM_1756297147"], d["UF_CRM_1756297147"])
        })

    return deals


@main_auth(on_start=True, set_cookie=True)
def last_deals(request):
    user = request.bitrix_user
    but = request.bitrix_user_token
    deals = get_user_deals(but, user.id)
    form = DealForm()
    return render(request, 'deals/index.html', {'user': user, 'deals': deals, 'form': form})


@main_auth(on_cookies=True)
def create_deal(request):
    user = request.bitrix_user
    but = request.bitrix_user_token

    if request.method == "POST":
        form = DealForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            date_create_iso = data["begin_date"].isoformat()

            fields = {
                "TITLE": data["title"],
                "STAGE_ID": data["stage_id"],
                "OPPORTUNITY": data["opportunity"],
                "BEGINDATE": date_create_iso,
                "UF_CRM_1756295581": int(data["payment_method"]),
                "UF_CRM_1756297147": int(data["delivery_method"]),
            }

            but.call_api_method("crm.deal.add", {"fields": fields})
            deals = get_user_deals(but, user.id)
            return render(request, "deals/index.html", {"form": form, "user": user, "deals": deals})
        else:
            print(form.errors)
    else:
        form = DealForm()

    deals = get_user_deals(but, user.id)
    return render(request, "deals/index.html", {"form": form, "user": user, "deals": deals})
