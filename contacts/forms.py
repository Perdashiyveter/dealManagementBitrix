from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField(
        label="Выберите CSV или XLSX файл",
        widget=forms.ClearableFileInput(attrs={"accept": ".csv, .xlsx"})
    )


class ExportFileForm(forms.Form):
    FORMAT_CHOICES = [
        ("csv", "CSV"),
        ("xlsx", "XLSX"),
    ]
    file_format = forms.ChoiceField(choices=FORMAT_CHOICES, label="Формат экспорта")