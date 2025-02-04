from django.contrib.auth.models import Group
from django.db import models
from django.contrib.auth.models import User
class Client(models.Model):

    STATUS_CHOICES = [
        ('lead', 'Лид'),
        ('client', 'Клиент'),
        ('customer', 'Заказчик'),
    ]

    # Основные данные клиента
    lead_number = models.AutoField(primary_key=True)  # Автоматическая нумерация лидов
    name = models.CharField(max_length=255)
    instagram_link = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='lead')
    manager = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)

    # Поля для контактов
    contact_1 = models.TextField(blank=True, null=True)
    contact_2 = models.TextField(blank=True, null=True)
    contact_3 = models.TextField(blank=True, null=True)
    contact_4 = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lead_number} - {self.name}"


class CustomTable(models.Model):
    name = models.CharField(max_length=255)  # Название таблицы
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания таблицы
    updated_at = models.DateTimeField(auto_now=True)  # Последнее обновление таблицы
    visible_fields = models.JSONField(default=list, blank=True)  # Отображаемые поля в формате списка
    # Например, одна группа на таблицу. Если нужно несколько групп, можно ManyToManyField.
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tables',
        verbose_name='Группа с доступом'
    )
    def __str__(self):
        return self.name

class CustomRow(models.Model):

    STATUS_CHOICES = [
        ('lead', 'Лид'),
        ('client', 'Клиент'),
        ('customer', 'Заказчик'),
    ]

    CONTACT_CHOICES = [
        ('contact_1', 'Контакт 1'),
        ('contact_2', 'Контакт 2'),
        ('contact_3', 'Контакт 3'),
        ('contact_4', 'Контакт 4'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]

    # Поля
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='lead',
        blank=True,
        null=True
    )
    contact = models.CharField(
        max_length=10,
        choices=CONTACT_CHOICES,
        blank=True,
        null=True
    )
    priority = models.CharField(
        max_length=12,
        choices=PRIORITY_CHOICES,
        default='low',
        blank=True,
        null=True
    )

    change_status_contact = models.CharField(
    max_length=10,
    choices=CONTACT_CHOICES,  # 👈 Добавляем `choices`
    blank=True,
    null=True
    )
    # Привязка к таблице
    table = models.ForeignKey(CustomTable, on_delete=models.CASCADE, related_name="rows", null=False, blank=False)

    # Фиксированные поля
    name = models.CharField(max_length=255)  # Имя клиента
    instagram_username = models.CharField(max_length=40, blank=True, null=True)  # Никнейм Instagram
    instagram_link = models.URLField(blank=True, null=True)  # Ссылка Instagram
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # Номер телефона
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name='Електронна пошта')
    manager = models.CharField(max_length=255)  # Менеджер (обязательное)
    country = models.CharField(max_length=255, blank=True, null=True)  # Поле страны
    city = models.CharField(max_length=255, blank=True, null=True)  # Поле города
    status = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('lead', 'Лид'),
        ('client', 'Клиент'),
        ('customer', 'Заказчик')
    ], default='lead')

    # Финансовые данные
    deal_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deal_amount_currency = models.CharField(max_length=3, choices=[('UAH', 'UAH'), ('USD', 'USD'), ('EUR', 'EUR')], default='UAH')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    paid_amount_currency = models.CharField(max_length=3, choices=[('UAH', 'UAH'), ('USD', 'USD'), ('EUR', 'EUR')], default='UAH')
    expected_profit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    expected_profit_currency = models.CharField(max_length=3, choices=[('UAH', 'UAH'), ('USD', 'USD'), ('EUR', 'EUR')], default='UAH')

    # Контакты
    contact = models.CharField(max_length=10, blank=True, null=True, choices=[
        ('contact_1', 'Контакт 1'),
        ('contact_2', 'Контакт 2'),
        ('contact_3', 'Контакт 3'),
        ('contact_4', 'Контакт 4'),
    ])
    change_status_contact = models.CharField(max_length=10, blank=True, null=True, choices=[
        ('contact_1', 'Контакт 1'),
        ('contact_2', 'Контакт 2'),
        ('contact_3', 'Контакт 3'),
        ('contact_4', 'Контакт 4'),
    ])

    priority = models.CharField(
        max_length=12,
        choices=[
            ('low', 'Низький'),
            ('medium', 'Середній'),
            ('high', 'Високий'),
        ],
        default='low',  # Значение по умолчанию
        verbose_name='Пріоритет'
    )

    # Даты
    record_date = models.DateTimeField()  # Дата записи
    due_date = models.DateTimeField(blank=True, null=True)  # Срок выполнения
    inquiry_date = models.DateTimeField(blank=True, null=True)  # Дата обращения

    # Новое поле для динамических данных
    additional_data = models.JSONField(default=dict, blank=True)  # Для хранения уникальных данных

    # Метаданные
    last_updated = models.DateTimeField(auto_now=True)  # Последнее изменение
    
    updated_by = models.ManyToManyField(
    User,
    blank=True,
    related_name='updated_rows',
    verbose_name="Змінено користувачем"
    )   
    def get_updated_by_display(self):
        """
        Возвращает пользователей в виде строки: "ANNA, PETRO"
        """
        return ", ".join(self.updated_by.values_list('username', flat=True)) 
      # Флаг для определения ручного изменения
    manually_updated = models.BooleanField(
        default=False, 
        verbose_name="Ручное изменение"
    )

    def __str__(self):
        return f"{self.name} - {self.table.name}"
