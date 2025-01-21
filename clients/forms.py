from django import forms
from .models import Client, CustomTable, CustomRow
import datetime


class ClientForm(forms.ModelForm):
    """
    Форма для работы с клиентами.
    """
    class Meta:
        model = Client
        fields = [
            'name', 'instagram_link', 'status', 'manager', 'city',
            'contact_1', 'contact_2', 'contact_3', 'contact_4'
        ]
        labels = {
            'name': "Ім'я клієнта",
            'instagram_link': "Посилання Instagram",
            'status': "Статус",
            'manager': "Менеджер",
            'city': "Місто",
            'contact_1': "Контакт 1",
            'contact_2': "Контакт 2",
            'contact_3': "Контакт 3",
            'contact_4': "Контакт 4",
        }
        widgets = {
            'instagram_link': forms.URLInput(attrs={'placeholder': 'https://instagram.com/...'}),
        }


class CustomTableForm(forms.ModelForm):
    """
    Форма для работы с таблицами.
    """
    class Meta:
        model = CustomTable
        fields = ['name', 'description']
        labels = {
            'name': "Назва таблиці",
            'description': "Опис таблиці",
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class CustomRowForm(forms.ModelForm):
    """
    Форма для работы со строками таблиц.
    """
    instagram_username = forms.CharField(
        label="Нікнейм Instagram",
        widget=forms.TextInput(attrs={
            'placeholder': '@username',
        }),
        required=False
    )
    # Поля для выбора валюты
    CURRENCY_CHOICES = [
        ('UAH', 'UAH'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    ]

    deal_amount_currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES, 
        label="Валюта суми угоди", 
        required=False
    )
    paid_amount_currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES, 
        label="Валюта оплаченої суми", 
        required=False
    )
    expected_profit_currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES, 
        label="Валюта очікуваного прибутку", 
        required=False
    )
    change_status_contact = forms.ChoiceField(
        choices=[
            ('contact_1', 'Контакт 1'),
            ('contact_2', 'Контакт 2'),
            ('contact_3', 'Контакт 3'),
            ('contact_4', 'Контакт 4'),
        ],
        label="Контакт для зміни статусу",
        required=False
    )

    country = forms.CharField(
        label="Країна",
        widget=forms.TextInput(attrs={
            'placeholder': 'Введіть країну',
        }),
        required=False  # Поле не обязательное
    )
    city = forms.CharField(
        label="Місто",
        widget=forms.TextInput(attrs={
            'placeholder': 'Введіть місто',
        }),
        required=False  # Поле не обязательное
    )

    priority = forms.ChoiceField(
        choices=[
            ('low', 'Низький'),
            ('medium', 'Середній'),
            ('high', 'Високий'),
        ],
        label="Пріоритет",
        required=False
    )

   

    class Meta:
        model = CustomRow
        exclude = ['table', 'last_updated']  # Исключаем поля, которые заполняются автоматически

        # Настройка виджетов
        widgets = {
            'record_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'due_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'inquiry_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

        # Метки полей
        labels = {
            'name': "Ім'я клієнта",
            'instagram_username': "никнейм Instagram",
            'instagram_link': "Посилання Instagram",
            'phone_number': "Номер телефону",
            'email': "Електрона пошта",
            'manager': "Менеджер",
            'status': "Статус",
            'city': "Місто",
            'email': "Електронна пошта",
            'comment': "Коментар",
            'record_date': "Дата запису",
            'due_date': "Дата виконання",
            'inquiry_date': "Дата звернення",
            'last_contact': "Останній контакт",
            'next_step': "Наступний крок",
            'communication_result': "Результат комунікації",
            'deal_amount': "Сума угоди",
            'paid_amount': "Оплачена сума",
            'expected_profit': "Очікуваний прибуток",
            'priority': "Пріоритет",
            'country': "Країна", 
        }

    def __init__(self, *args, **kwargs):
        """
        Инициализация формы. Устанавливаем начальные значения для валют.
        """
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['deal_amount_currency'].initial = self.instance.deal_amount_currency or 'UAH'
            self.fields['paid_amount_currency'].initial = self.instance.paid_amount_currency or 'UAH'
            self.fields['expected_profit_currency'].initial = self.instance.expected_profit_currency or 'UAH'

    def clean(self):
        """
        Валидация данных формы.
        """
        cleaned_data = super().clean()
        instagram_username = cleaned_data.get('instagram_username')
        phone_number = cleaned_data.get('phone_number')

        # Проверяем, что заполнено хотя бы одно из полей
        if not instagram_username and not phone_number:
            raise forms.ValidationError("Потрібно вказати або нікнейм Instagram, або номер телефону.")
        instagram_username = self.cleaned_data.get('instagram_username')
        if instagram_username and not instagram_username.startswith('@'):
            raise forms.ValidationError("Нікнейм Instagram має починатися з символу '@'.")
       

        # Проверяем сумму на отрицательные значения
        deal_amount = cleaned_data.get('deal_amount')
        paid_amount = cleaned_data.get('paid_amount')
        expected_profit = cleaned_data.get('expected_profit')


        if deal_amount is not None and deal_amount < 0:
            self.add_error('deal_amount', "Сума угоди не може бути від'ємною.")
        if paid_amount is not None and paid_amount < 0:
            self.add_error('paid_amount', "Оплачена сума не може бути від'ємною.")
        if expected_profit is not None and expected_profit < 0:
            self.add_error('expected_profit', "Очікуваний прибуток не може бути від'ємним.")

        # Проверяем последовательность дат
        record_date = cleaned_data.get('record_date')
        due_date = cleaned_data.get('due_date')
        inquiry_date = cleaned_data.get('inquiry_date')

        if not record_date:
            self.add_error('record_date', "Дата запису є обов'язковою.")
        if due_date and record_date and due_date < record_date:
            self.add_error('due_date', "Дата виконання не може бути раніше дати запису.")

        return cleaned_data