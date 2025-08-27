from django import forms

STAGE_CHOICES = [
    ("NEW", "Новая сделка"),
    ("PREPARATION", "Подготовка документов"),
    ("PREPAYMENT_INVOICE", "Счёт на предоплату"),
    ("EXECUTING", "В работе"),
    ("FINAL_INVOICE", "Финальный счёт"),
]

PAYMENT_CHOICES = [
    (45, "Наличные"),
    (47, 'Банковская карта'),
    (49, "СБП"),
]

DELIVERY_CHOICES = [
    (51, 'Курьер'),
    (53, 'Самовывоз'),
    (55, 'Пункт выдачи (Яндекс.Маркет, Boxberry)'),
    (57, 'Пункт выдачи (CДЭК)'),
    (59, 'Почта России'),
]


class DealForm(forms.Form):
    title = forms.CharField(label="Название сделки", max_length=255)
    stage_id = forms.ChoiceField(label="Этап", choices=STAGE_CHOICES)
    begin_date = forms.DateTimeField(label="Дата начала сделки",
        input_formats=['%Y-%m-%d'],
        widget=forms.DateTimeInput(attrs={'type': 'date'})
    )
    opportunity = forms.DecimalField(label="Сумма", min_value=0)
    payment_method = forms.ChoiceField(label="Способ оплаты", choices=PAYMENT_CHOICES)
    delivery_method = forms.ChoiceField(label="Способ доставки", choices=DELIVERY_CHOICES)