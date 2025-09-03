import base64
from django.shortcuts import render, get_object_or_404
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from .models import QRCode
import qrcode
import io


# Create your views here.
def get_products(but):
    response = but.call_list_method('catalog.product.list', {
        'filter': {'iblockId': 15},
        'order': {'id': 'desc'},
        'select': ['id', 'iblockId', 'name', 'property55', 'detailText', 'property45'],
        'start': 0
    })

    # # Узнал Id "Стоимость"
    # response2 = but.call_list_method('catalog.product.getFieldsByFilter', {
    #     'filter': {'iblockId': 15}
    # })
    #
    # print(response2)
    # for key, value in response2['product'].items():
    #     print(f"Ключ: {key}")
    #     print(f"Значение: {value}")
    #     print("------")

    products = []
    for product in response['products']:
        images = but.call_list_method('catalog.productImage.list', fields={'productId': product['id']})['productImages']
        products.append({
            'ID': product['id'],
            'NAME': product['name'],
            'PRICE': "{:.2f}".format(float(product['property55']['value'].split('|')[0])),
            'DESCRIPTION': product['detailText'],
            'IMAGE': images[0]['detailUrl']
        })

    return products


@main_auth(on_cookies=True)
def show_catalog(request):
    but = request.bitrix_user_token
    products = get_products(but)

    return render(request, 'qrapp/catalog.html', {'products': products})


@main_auth(on_cookies=True)
def index(request):
    but = request.bitrix_user_token
    if request.method == "POST":
        try:
            product_id = int(request.POST.get("product_id"))

            products = {p['ID']: p for p in get_products(but)}
            product_details = products[product_id]

            if product_id:
                qr_obj = QRCode.objects.create(
                    product_id=product_id,
                    name=product_details['NAME'],
                    description=product_details['DESCRIPTION'],
                    price=product_details['PRICE'],
                    photo_url=product_details['IMAGE']
                )
                link = request.build_absolute_uri(f"product/{qr_obj.uuid}")

                qr = qrcode.make(link)
                buf = io.BytesIO()
                qr.save(buf, format="PNG")
                qr_img = base64.b64encode(buf.getvalue()).decode("utf-8")

            return render(request, "qrapp/index.html", {
                'qr_img': qr_img,
                'link': link,
                'product_id': product_id
            })

        except:
            error_message = "Товара с таким ID не существует"
            return render(request, "qrapp/index.html", {
                'error_message': error_message
            })

    return render(request, "qrapp/index.html")


def product_detail(request, uuid):
    qr_obj = get_object_or_404(QRCode, uuid=uuid)

    return render(request, "qrapp/product_detail.html", {
        "product": qr_obj,
        "uuid": uuid,
    })





