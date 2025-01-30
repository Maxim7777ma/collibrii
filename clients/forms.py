from django import forms
from .models import Client, CustomTable, CustomRow
import datetime
import json
from datetime import date
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.core.serializers.json import DjangoJSONEncoder
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





FIELD_TRANSLATIONS = {
    'name': "Ім'я клієнта",
    'instagram_username': "Нікнейм Instagram",
    'instagram_link': "Посилання Instagram",
    'phone_number': "Номер телефону",
    'email': "Електронна пошта",
    'manager': "Менеджер",
    'country': "Країна",
    'city': "Місто",
    'status': "Статус",
    'deal_amount': "Сума угоди",
    'paid_amount': "Оплачена сума",
    'expected_profit': "Очікуваний прибуток",
    'contact': "Контакт",
    'change_status_contact': "Змінити статус контакту",
    'priority': "Пріоритет",
    'record_date': "Дата запису",
    'due_date': "Дата виконання",
    'inquiry_date': "Дата звернення",
    'additional_data': "Додаткові дані",
    'last_updated': "Останнє оновлення",
    'updated_by': "Змінено користувачем",
    'manually_updated': "Ручна зміна користувача",
    
}

class CustomTableForm(forms.ModelForm):
    """
    Форма для создания и редактирования таблиц.
    """
    # Список полей из модели CustomRow
    FIELD_CHOICES = [
        (field.name, FIELD_TRANSLATIONS.get(field.name, field.verbose_name))
        for field in CustomRow._meta.fields
        if field.name not in ['id', 'table', 'deal_amount_currency', 'paid_amount_currency', 'expected_profit_currency']
    ]+ [
    ('updated_by', FIELD_TRANSLATIONS.get('updated_by', 'Updated By')),
    
]


    visible_fields = forms.MultipleChoiceField(
        choices=FIELD_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Выберите поля для отображения"
    )

    class Meta:
        model = CustomTable
        fields = ['name', 'description', 'visible_fields', 'group']
        labels = {
            'name': "Назва таблиці",
            'description': "Опис таблиці",
            'visible_fields': "Оберіть поля для відображення",
        }
        help_texts = {
            'name': "Введіть унікальну назву для таблиці.",
            'description': "Опишіть призначення таблиці (необов'язково).",
            'visible_fields': "Виберіть лише ті поля, які повинні бути видимі.",
        }

    def __init__(self, *args, **kwargs):
        """
        Исключаем ненужные поля валют из выбора.
        """
        super().__init__(*args, **kwargs)
        # Фильтруем только нужные поля для отображения
        exclude_fields = ['deal_amount_currency', 'paid_amount_currency', 'expected_profit_currency']
        self.fields['visible_fields'].choices = [
            choice for choice in self.fields['visible_fields'].choices if choice[0] not in exclude_fields
        ]

class CustomRowForm(forms.ModelForm):
    """
    Форма для работы со строками таблиц.
    """



    def __init__(self, *args, table=None, user=None, **kwargs):
        """
        Создание формы. Если передана таблица, генерируем дополнительные поля.
        """
        
        
        super().__init__(*args, **kwargs)
        self.table = table
        self.user = user  # Текущий пользователь
        additional_data = {}
        
        
          # Определяем QuerySet для поля `updated_by`
        if table and table.group:
            queryset = table.group.user_set.all()  # Ограничиваем пользователей группой
        else:
            queryset = User.objects.all()  # Используем всех пользователей

        initial_users = self.instance.updated_by.all() if self.instance.pk else []    

        

        # Поле для ручного управления
        self.fields['manually_updated'] = forms.BooleanField(
            required=False,
            label="Ручное изменение",
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
        )

        # Поле для выбора пользователей
        self.fields['updated_by'] = forms.ModelMultipleChoiceField(
            queryset=User.objects.all(),
            required=False,
            label="Змінено користувачем",
            widget=forms.SelectMultiple(attrs={'class': 'form-control'})
        )
       # Если ручное управление выключено, скрываем поле updated_by
        if not self.instance.manually_updated:
            self.fields['updated_by'].widget.attrs['hidden'] = True
            self.fields['updated_by'].disabled = True
        
        if isinstance(self.instance.additional_data, str):
            try:
                additional_data = json.loads(self.instance.additional_data)
            except json.JSONDecodeError:
                additional_data = {}
        else:
            additional_data = self.instance.additional_data or {}

        
        
        for date_field in ['record_date', 'due_date', 'inquiry_date']:
            date_value = additional_data.get(date_field)
            # Добавляем поле с `TextInput`, формат для пользователя `ДД-ММ-ГГГГ`
            self.fields[date_field] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ДД-ММ-ГГГГ'}),
            label=FIELD_TRANSLATIONS.get(date_field, date_field)
        )

            if date_value:
                try:
                    parsed_date = datetime.datetime.strptime(date_value, '%d-%m-%Y').date()
                    self.fields[date_field].initial = parsed_date.strftime('%d-%m-%Y')  # Оставляем формат "ДД-ММ-ГГГГ"
                except ValueError:
                    self.fields[date_field].initial = None  # Если дата битая, пусть будет пустая
       
        
       # Генерация динамических полей из table.visible_fields
        if table and table.visible_fields:
            for field in table.visible_fields:
                # Если поле представлено как словарь (например, {"name": "deal_amount"})
                if isinstance(field, dict):
                    field_name = field.get('name')
                else:
                    field_name = field

                # Получаем перевод для метки
                field_label = FIELD_TRANSLATIONS.get(field_name, field_name)

                # Добавляем поля по типу
                if field_name in ['deal_amount', 'paid_amount', 'expected_profit']:
                    self.fields[field_name] = forms.DecimalField(label=field_label, required=False)
                elif field_name in ['record_date', 'due_date', 'inquiry_date']:
                    self.fields[field_name] = forms.DateField(
                    label=field_label,
                    widget=forms.DateInput(attrs={'type': 'date'}),
                    required=False
                )
                elif field_name == 'status':  # Для выпадающего списка "Статус"
                    self.fields[field_name] = forms.ChoiceField(
                    label=field_label,
                    choices=CustomRow.STATUS_CHOICES,
                    widget=forms.Select(attrs={'class': 'form-control'}),
                    required=False
                )
                elif field_name == 'contact':  # Для выпадающего списка "Контакт"
                    self.fields[field_name] = forms.ChoiceField(
                    label=field_label,
                    choices=CustomRow.CONTACT_CHOICES,
                    widget=forms.Select(attrs={'class': 'form-control'}),
                    required=False
                )
                elif field_name == 'priority':  # Для выпадающего списка "Приоритет"
                    self.fields[field_name] = forms.ChoiceField(
                    label=field_label,
                    choices=CustomRow.PRIORITY_CHOICES,
                    widget=forms.Select(attrs={'class': 'form-control'}),
                    required=False
                ) 
                elif field_name == 'updated_by':
                    self.fields[field_name] = forms.ModelMultipleChoiceField(
                    queryset=queryset,
                    required=False,
                    initial=initial_users,
                    widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
                    label=FIELD_TRANSLATIONS.get(field_name, field_name)
                )
                elif field_name == 'manually_updated':
                    self.fields[field_name] = forms.BooleanField(
                    required=False,
                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                    label=FIELD_TRANSLATIONS.get(field_name, field_name)
                )

                else:
                    self.fields[field_name] = forms.CharField(label=field_label, required=False)
        
        # Устанавливаем начальные значения для фиксированных валют
        if self.instance and self.instance.pk:
            self.fields['deal_amount_currency'].initial = self.instance.deal_amount_currency or 'UAH'
            self.fields['paid_amount_currency'].initial = self.instance.paid_amount_currency or 'UAH'
            self.fields['expected_profit_currency'].initial = self.instance.expected_profit_currency or 'UAH'

    def clean_updated_by(self):
        manually_updated = self.cleaned_data.get('manually_updated', False)
        selected_users = self.cleaned_data.get('updated_by')

        if manually_updated:
            if not selected_users:
                self.add_error('updated_by', "Оберіть хоча б одного користувача.")
                return []
            return selected_users  # ✅ Сохраняем выбранных пользователей

        # ✅ Если вручную ничего не выбрано, ставим только текущего пользователя
        return selected_users if selected_users else [self.user]
    
    def save(self, commit=True, user=None):
        """
        Сохранение формы. Динамические поля сохраняются в additional_data.
        """
        instance = super().save(commit=False)
        additional_data = {}

        model_fields = self._meta.fields if hasattr(self._meta, 'fields') else []
        if model_fields is None:
            model_fields = []

    # Сохраняем только динамические данные
        for field_name in self.fields:
            if field_name not in model_fields:  # Только динамические поля
                value = self.cleaned_data[field_name]

                # Преобразуем дату в строку
                # ✅ Дата сохраняется в формате "ДД-ММ-ГГГГ"
                if isinstance(value, datetime.date):
                    additional_data[field_name] = value.strftime('%d-%m-%Y')

                    # ✅ Если строка, пробуем конвертировать
                elif isinstance(value, str):
                    try:
                        parsed_date = datetime.datetime.strptime(value, '%d-%m-%Y').date()
                        additional_data[field_name] = parsed_date.strftime('%d-%m-%Y')
                    except ValueError:
                        additional_data[field_name] = value  # Сохраняем как есть, если это не дата

                # ✅ Если поле - объект User → сохраняем username
                elif isinstance(value, User):
                    value = str(value.id)

                # ✅ Если поле - QuerySet пользователей → преобразуем в список ID
                elif isinstance(value, QuerySet) and value.model == User:
                    value = list(map(str, value.values_list('id', flat=True)))

                # ✅ Если поле - список пользователей → преобразуем в список ID
                elif isinstance(value, list):
                    value = [str(user.id) if isinstance(user, User) else str(user) for user in value]

                # Добавляем значение в additional_data
                additional_data[field_name] = value

        # ✅ Сериализуем additional_data в JSON
        instance.additional_data = json.dumps(additional_data, cls=DjangoJSONEncoder)

        if commit:
            instance.save()

           # ✅ Берём список выбранных пользователей или текущего пользователя
            selected_users = self.cleaned_data.get("updated_by", [self.user])

            # ✅ Если `selected_users` - QuerySet, преобразуем его в список ID
            selected_users = list(selected_users.values_list("id", flat=True)) if isinstance(selected_users, QuerySet) else [
            user.id if isinstance(user, User) else user for user in selected_users
            ]

            # ✅ Обновляем `updated_by`
            instance.updated_by.set(User.objects.filter(id__in=selected_users))


        return instance
    
    def clean(self):
        """
        Валидация данных формы.
        """
        cleaned_data = super().clean()
        instagram_username = cleaned_data.get('instagram_username')
        phone_number = cleaned_data.get('phone_number')
        manually_updated = cleaned_data.get("manually_updated")
        updated_by = cleaned_data.get("updated_by")

        # Если ручное управление выключено, добавляем текущего пользователя
        if not manually_updated:
            cleaned_data['updated_by'] = User.objects.filter(id=self.user.id) if self.user else User.objects.none()
        else:
        # Если ручное управление включено, но пользователи не выбраны, выдаём ошибку
            if not updated_by:
                self.add_error('updated_by', "Оберіть хоча б одного користувача.")

        

        # Проверяем, что заполнено хотя бы одно из полей
        if not instagram_username and not phone_number:
            raise forms.ValidationError("Потрібно вказати або нікнейм Instagram, або номер телефону.")
        if instagram_username and not instagram_username.startswith('@'):
            raise forms.ValidationError("Нікнейм Instagram має починатися з символу '@'.")

        # Проверяем суммы на отрицательные значения
        deal_amount = cleaned_data.get('deal_amount')
        paid_amount = cleaned_data.get('paid_amount')
        expected_profit = cleaned_data.get('expected_profit')

        if deal_amount is not None and deal_amount < 0:
            self.add_error('deal_amount', "Сума угоди не може бути від'ємною.")
        if paid_amount is not None and paid_amount < 0:
            self.add_error('paid_amount', "Оплачена сума не може бути від'ємною.")
        if expected_profit is not None and expected_profit < 0:
            self.add_error('expected_profit', "Очікуваний прибуток не може бути від'ємним.")

        # Проверяем даты на корректность
        record_date = cleaned_data.get('record_date')
        due_date = cleaned_data.get('due_date')
        if not record_date:
            self.add_error('record_date', "Дата запису є обов'язковою.")
        if due_date and record_date and due_date < record_date:
            self.add_error('due_date', "Дата виконання не може бути раніше дати запису.")

        return cleaned_data

    class Meta:
        model = CustomRow
        exclude = ['table', 'additional_data', 'last_updated']  # Исключаем технические поля

        # Настройка виджетов
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'contact': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            # 'record_date': forms.DateInput(attrs={'type': 'date'}, format='%d-%m-%Y'),
            # 'due_date': forms.DateInput(attrs={'type': 'date'}, format='%d-%m-%Y'),
            # 'inquiry_date': forms.DateInput(attrs={'type': 'date'}, format='%d-%m-%Y'),
            'updated_by': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'manually_updated': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
       
        # Метки полей
        labels = FIELD_TRANSLATIONS  # Используем тот же словарь переводов
        