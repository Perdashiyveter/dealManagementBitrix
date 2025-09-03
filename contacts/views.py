from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from .forms import UploadFileForm, ExportFileForm
from .services import parsers, exporters


@main_auth(on_cookies=True)
def index(request):
    return render(request, 'contacts/index.html')


@main_auth(on_cookies=True)
def import_contacts(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        but = request.bitrix_user_token

        if form.is_valid():
            file = request.FILES["file"]

            if file.name.endswith(".csv"):
                parser = parsers.CSVParser()
            elif file.name.endswith(".xlsx"):
                parser = parsers.XLSXParser()
            else:
                error = "Неверный формат файла"
                return render(request, "contacts/import.html", {
                    'form': form,
                    'error': error
                })

            rows = parser.parse(file)
            companies = but.call_list_method('crm.company.list', {
                'select': ['ID','TITLE']
            })

            batch_size = 50
            batches = [rows[i:i+batch_size] for i in range(0, len(rows), batch_size)]

            info = {
                'accepted': 0,
                'rejected': 0
            }

            for batch in batches:
                methods = []
                existing_contacts = but.call_list_method('crm.contact.list', {
                    'select': ['ID', 'EMAIL', 'PHONE']
                })
                email_set = set()
                phone_set = set()
                for c in existing_contacts:
                    for e in c.get('EMAIL', []):
                        email_set.add(e['VALUE'].lower())
                    for p in c.get('PHONE', []):
                        phone_set.add(p['VALUE'])

                for i, row in enumerate(batch):
                    row = {k.lower(): v for k, v in row.items()}

                    row['номер телефона'] = '+'+str(row['номер телефона'])
                    try:
                        row['компания'] = [x for x in companies if x['TITLE']==row['компания']][0].get('ID', '')
                    except:
                        info['rejected'] += 1
                        continue

                    if row['почта'].lower() in email_set or row['номер телефона'] in phone_set:
                        info['rejected'] += 1
                        continue

                    email_set.add(row['почта'])
                    phone_set.add(row['номер телефона'])

                    methods.append((
                        f"contact_add_{i}",
                        'crm.contact.add', {
                            'fields': {
                                'NAME': row['имя'],
                                'LAST_NAME': row['фамилия'],
                                'COMPANY_ID': int(row['компания']),
                                'PHONE': [
                                    {
                                        'VALUE': row['номер телефона'],
                                        'VALUE_TYPE': "MOBILE",
                                    },
                                ],
                                'EMAIL': [
                                    {
                                        'VALUE': row['почта'],
                                        'VALUE_TYPE': "MAILING",
                                    },
                                ]
                            }
                        }
                    ))
                but.batch_api_call(methods)
                info['accepted'] += len(methods)

    else:
        form = UploadFileForm()
        info = {}

    return render(request, "contacts/import.html", {
        'form': form,
        'info': info
    })


@main_auth(on_cookies=True)
def export_contacts(request):
    if request.method == "POST":
        form = ExportFileForm(request.POST)
        but = request.bitrix_user_token
        if form.is_valid():
            fmt = form.cleaned_data['file_format']

            contacts = but.call_list_method('crm.contact.list', {
                    'select': ['ID', 'NAME', 'LAST_NAME', 'EMAIL', 'PHONE', 'COMPANY_ID']
            })

            companies = but.call_list_method('crm.company.list', {
                'select': ['ID', 'TITLE']
            })

            companies = {item['ID']: item['TITLE'] for item in companies}

            for c in contacts:
                c['COMPANY_ID'] = companies[c['COMPANY_ID']]

            if fmt == 'csv':
                exporter = exporters.CSVExporter()
                content = exporter.export(contacts)
                response = HttpResponse(content, content_type="text/csv")
                response["Content-Disposition"] = 'attachment; filename="contacts.csv"'
                return response
            if fmt == 'xlsx':
                exporter = exporters.XLSXExporter()
                content = exporter.export(contacts)
                response = HttpResponse(content, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                response["Content-Disposition"] = 'attachment; filename="contacts.xlsx"'
                return response

    else:
        form = ExportFileForm()
    return render(request, 'contacts/export.html', {
        'form': form
    })

