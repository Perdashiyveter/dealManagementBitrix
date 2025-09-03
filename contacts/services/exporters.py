import csv
import openpyxl
import io


class BaseExporter:
    def export(self, contacts):
        raise NotImplementedError


class CSVExporter(BaseExporter):
    def export(self, contacts):
        headers = ["Имя", "Фамилия", "Номер телефона", "Почта", "Компания"]

        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow(headers)

        for c in contacts:
            name = c.get("NAME")
            last_name = c.get("LAST_NAME", "")
            phones = ', '.join([p.get("VALUE", '').replace('+', '') for p in c.get("PHONE", [])])
            emails = ', '.join([e.get("VALUE", '') for e in c.get("EMAIL", [])])
            company = c.get("COMPANY_ID", "")

            writer.writerow([name, last_name, phones, emails, company])

        return buffer.getvalue().encode("utf-8-sig")


class XLSXExporter(BaseExporter):
    def export(self, contacts):
        wb = openpyxl.Workbook()
        ws = wb.active
        headers = ["Имя", "Фамилия", "Номер телефона", "Почта", "Компания"]
        ws.append(headers)

        for c in contacts:
            name = c.get("NAME")
            last_name = c.get("LAST_NAME", "")
            phones = ', '.join([p.get("VALUE", '').replace('+', '') for p in c.get("PHONE", [])])
            emails = ', '.join([e.get("VALUE", '') for e in c.get("EMAIL", [])])
            company = c.get("COMPANY_ID", "")

            ws.append([name, last_name, phones, emails, company])

        buf = io.BytesIO()
        wb.save(buf)

        return buf.getvalue()
