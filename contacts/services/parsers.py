import csv
import openpyxl


class BaseParser:
    def parse(self, file):
        raise NotImplementedError


class CSVParser(BaseParser):
    def parse(self, file):
        decoded = file.read().decode("utf-8-sig").splitlines()
        reader = csv.DictReader(decoded, delimiter=";")
        return list(reader)


class XLSXParser(BaseParser):
    def parse(self, file):
        wb = openpyxl.load_workbook(file)
        sheet = wb.active
        headers = [cell.value for cell in sheet[1]]
        rows = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            rows.append(dict(zip(headers, row)))
        return rows


