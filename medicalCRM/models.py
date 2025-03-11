from django.db import models
from django.contrib.auth.models import User
from datetime import date




from django.db import models



# 📌 Модель для услуг с уникальным кодом
class ServicePriceList(models.Model):
    service_code = models.CharField(max_length=50, unique=True, verbose_name="Код услуги")  # Уникальный код услуги
    service_name = models.CharField(max_length=255, verbose_name="Название услуги")  # Название услуги
    service_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена услуги")  # Стоимость

    def __str__(self):
        return f"{self.service_code} - {self.service_name} ({self.service_price} грн)"

    class Meta:
        verbose_name = "Прайс-лист услуги"
        verbose_name_plural = "Прайс-лист услуг"

# 📌 Модель филиала клиники
class ClinicBranch(models.Model):
    branch_name = models.CharField(max_length=100, verbose_name="Название филиала")  # Название филиала
    branch_address = models.CharField(max_length=255, verbose_name="Адрес филиала")  # Адрес филиала
    work_schedule = models.JSONField(blank=True, null=True, verbose_name="График работы")  # График работы в формате JSON

    def __str__(self):
        return self.branch_name
    class Meta:
        verbose_name = "Филиал клиники"
        verbose_name_plural = "Филиалы клиники"

    def get_work_schedule_display(self):
        """Метод для удобного отображения расписания"""
        if self.work_schedule:
            return "\n".join([f"{day}: {hours}" for day, hours in self.work_schedule.items()])
        return "График не указан"
    




# 📌 Кабинеты клиники (связаны с филиалами)
class ClinicRoom(models.Model):
    branch = models.ForeignKey(ClinicBranch, on_delete=models.CASCADE, related_name='rooms', verbose_name="Филиал")  # Привязка к филиалу
    room_number = models.CharField(max_length=50, verbose_name="Номер кабинета")  # Номер кабинета

    def __str__(self):
        return f"{self.branch.branch_name} - Кабинет {self.room_number}"
    
    class Meta:
        verbose_name = "Кабинет"
        verbose_name_plural = "Кабинеты"


class Specialization(models.Model):
    name = models.CharField(max_length=100, verbose_name="Специализация")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Специализация"
        verbose_name_plural = "Специализации"


# 📌 Врачи (могут работать в разных филиалах и кабинетах, предоставлять разные услуги)
class Doctor(models.Model):
    fool_name = models.CharField(max_length=400, verbose_name="Полное ФИО", default="Имя не указано")
    gender = models.CharField(max_length=10, choices=[('male', 'Мужской'), ('female', 'Женский')], verbose_name="Пол")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    
    # 📌 Контактная информация
    phone_number_1 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон 1")
    phone_number_2 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон 2")
    phone_number_3 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон 3")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адрес")


    gender = models.CharField(max_length=10, choices=[('male', 'Мужской'), ('female', 'Женский')], verbose_name="Пол")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    photo = models.ImageField(upload_to='doctors_photos/', blank=True, null=True, verbose_name="Фото")

    branch = models.ForeignKey(ClinicBranch, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Филиал работы")
    room = models.ForeignKey(ClinicRoom, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Кабинет")
    services = models.ManyToManyField(ServicePriceList, blank=True, verbose_name="Оказываемые услуги")  # Услуги врача (может быть много)


    @property
    def age(self):
        """Автоматически вычисляет возраст на основе даты рождения"""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None


    # 📌 Медицинская информация
    specializations = models.ManyToManyField(Specialization, verbose_name="Специализации")
    education = models.TextField(blank=True, null=True, verbose_name="Образование")
    experience_years = models.PositiveIntegerField(blank=True, null=True, verbose_name="Опыт (лет)")
    certifications = models.TextField(blank=True, null=True, verbose_name="Сертификаты")# надо изображпнием сделать
    languages = models.CharField(max_length=255, blank=True, null=True, verbose_name="Языки")

        # 📌 Рабочий график
    work_schedule = models.JSONField(blank=True, null=True, verbose_name="Рабочий график")

    # 📌 Прочая информация
    notes = models.TextField(blank=True, null=True, verbose_name="Заметки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")



    car_number_1 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер автомобиля 1")
    car_number_2 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер автомобиля 2")


    # 📌 Соцсети
    instagram_username = models.CharField(max_length=100, blank=True, null=True, verbose_name="Instagram Ник")
    instagram_link = models.URLField(blank=True, null=True, verbose_name="Instagram Ссылка")
    instagram_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Instagram Телефон")

    telegram_username = models.CharField(max_length=100, blank=True, null=True, verbose_name="Telegram Ник")
    telegram_link = models.URLField(blank=True, null=True, verbose_name="Telegram Ссылка")
    telegram_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telegram Телефон")

    facebook_username = models.CharField(max_length=100, blank=True, null=True, verbose_name="Facebook Ник")
    facebook_link = models.URLField(blank=True, null=True, verbose_name="Facebook Ссылка")
    facebook_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Facebook Телефон")

    whatsapp_username = models.CharField(max_length=100, blank=True, null=True, verbose_name="WhatsApp Ник")
    whatsapp_link = models.URLField(blank=True, null=True, verbose_name="WhatsApp Ссылка")
    whatsapp_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="WhatsApp Телефон")

    viber_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Viber Телефон")

    branch_work = models.CharField(max_length=255, blank=True, null=True, verbose_name="Филиал работы")

    branch_work2 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Филиал работы2")

    branch_work3 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Филиал работы3")
    # 📌 Связь с филиалом и кабинетом
    branch = models.ForeignKey(ClinicBranch, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors', verbose_name="Филиал")
    room = models.ForeignKey(ClinicRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors', verbose_name="Кабинет")
    services = models.ManyToManyField(ServicePriceList, verbose_name="Оказанные услуги")  # Услуги, оказанные пациенту
    # услуги номер услуги название услуги цена услуги


    def __str__(self):
        return f"{self.fool_name}"
    
    class Meta:
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"

# 📌 Медсестры (привязаны к филиалам и кабинетам)
class Nurse(models.Model):
    fool_name = models.CharField(max_length=400, verbose_name="Полное ФИО", default="Имя не указано")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    branch = models.ForeignKey(ClinicBranch, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Филиал работы")
    room = models.ForeignKey(ClinicRoom, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Кабинет")

    def __str__(self):
        return f"{self.fool_name}"

    class Meta:
        verbose_name = "Медсестра"
        verbose_name_plural = "Медсестры"


# 📌 Запись на визит
class VisitRecord(models.Model):
    RECORD_STATUS = [
        ('pending', 'В обработке'),  # Запись создана, но еще не подтверждена
        ('paid', 'Предоплата'),  # Частичная оплата
        ('completed', 'Проведено'),  # Услуга оказана, но не оплачена полностью
        ('paid_finish', 'Оплачено'),  # Полная оплата -> Запись переносится в историю
    ]

    patient = models.ForeignKey('Pacient', on_delete=models.CASCADE, verbose_name="Пациент")  # Пациент
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Врач")  # Врач
    nurse = models.ForeignKey(Nurse, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Медсестра")  # Медсестра
    visit_date = models.DateField(verbose_name="Дата визита")  # Дата приема
    visit_time = models.TimeField(verbose_name="Время визита")  # Время приема

    visit_end_time = models.TimeField(verbose_name="Время окончания", null=True, blank=True)
    
    duration_minutes = models.PositiveIntegerField(verbose_name="Продолжительность (в минутах)", default=10)


    services = models.ManyToManyField(ServicePriceList, verbose_name="Оказанные услуги", blank=True)  # Услуги, оказанные пациенту
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая стоимость визита")  # Итоговая сумма визита
    payment_status = models.CharField(max_length=20, choices=RECORD_STATUS, default='pending', verbose_name="Статус визита")  # Текущий статус
    is_online = models.BooleanField(default=False, verbose_name="Онлайн прием")  # Онлайн или обычный прием

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")  # Дата создания
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления записи")  # Дата обновления

    description = models.TextField(blank=True, null=True, verbose_name="Описание визита")  # Описание записи

    clinic_branch = models.ForeignKey(
        'ClinicBranch', 
        on_delete=models.CASCADE, 
        verbose_name="Филиал",
        null=True, blank=True
    )  # Филиал клиники, где проводится приём

    clinic_room = models.ForeignKey(
        'ClinicRoom', 
        on_delete=models.CASCADE, 
        verbose_name="Кабинет",
        null=True, blank=True
    )  # Кабинет внутри филиала

    def save(self, *args, **kwargs):
        """Автоматически рассчитываем `visit_end_time` при сохранении"""
        if self.visit_time and self.duration_minutes:
            from datetime import timedelta, datetime
            if isinstance(self.visit_date, str):
                self.visit_date = datetime.strptime(self.visit_date, "%Y-%m-%d").date()

            if isinstance(self.visit_time, str):
                self.visit_time = datetime.strptime(self.visit_time, "%H:%M").time()
                # Проверка, что `duration_minutes` не выходит за границы

            if self.duration_minutes and self.duration_minutes > 1440:  # 1440 минут = 24 часа
                self.duration_minutes = 1440  # Ограничиваем максимальное значение до суток
                # 🛠 **Исправление: если `duration_minutes` отрицательный, делаем его 0**
            if self.duration_minutes < 0:
                self.duration_minutes = 0
                    
    
            visit_start = datetime.combine(self.visit_date, self.visit_time)
            self.visit_end_time = (visit_start + timedelta(minutes=self.duration_minutes)).time()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient} - {self.doctor} ({self.visit_date} {self.visit_time}) ({self.duration_minutes} мин)"

    class Meta:
        verbose_name = "Запись на прием"
        verbose_name_plural = "Записи на прием"

# 📌 История визитов (после полной оплаты)
class VisitHistory(models.Model):
    patient = models.ForeignKey('Pacient', on_delete=models.CASCADE, verbose_name="Пациент")  # Пациент
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Врач")  # Врач
    nurse = models.ForeignKey(Nurse, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Медсестра")  # Медсестра
    visit_date = models.DateField(verbose_name="Дата визита")  # Дата приема
    visit_time = models.TimeField(verbose_name="Время визита")  # Время приема
    services = models.ManyToManyField(ServicePriceList, verbose_name="Оказанные услуги")  # Услуги пациента
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая стоимость визита")  # Итоговая сумма визита
    is_online = models.BooleanField(default=False, verbose_name="Онлайн прием")  # Был ли прием онлайн

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления в историю")  # Дата переноса в историю

    def __str__(self):
        return f"История {self.id} - {self.patient} ({self.visit_date})"

    class Meta:
        verbose_name = "История визита"
        verbose_name_plural = "История визитов"

class Pacient(models.Model):
    # 📌 Основная информация
    fool_name = models.CharField(max_length=400, verbose_name="Полное ФИО", default="Имя не указано")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")

    # 📌 Телефоны (основные + соцсети)
    phone_number_1 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон 1")
    phone_number_2 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон 2")
    phone_number_3 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон 3")

    # 📌 Медицинская информация
    medical_card_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер медицинской карты")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    attending_doctor = models.CharField(max_length=255, blank=True, null=True, verbose_name="Лечащий врач")

    @property
    def age(self):
        """Автоматически вычисляет возраст на основе даты рождения"""
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    # 📌 Транспорт
    car_number_1 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер автомобиля 1")
    car_number_2 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер автомобиля 2")
    car_number_3 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер автомобиля 3")

    # 📌 Страховка
    insurance_policy_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Номер страхового полиса")
    insurance_policy_file = models.FileField(upload_to="insurance_policies/", blank=True, null=True, verbose_name="Файл страхового полиса (PDF)")

    # 📌 Скидочная карта
    discount_card = models.PositiveIntegerField(default=0, verbose_name="Скидочная карта (0-100%)")
    is_permanent_discount = models.BooleanField(default=False, verbose_name="Постоянная скидка")

    # 📌 VIP-клиент
    is_vip = models.BooleanField(default=False, verbose_name="VIP клиент")

    # 📌 Кредит
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Кредитная задолженность")

    # 📌 Комментарии
    notes = models.TextField(max_length=300, blank=True, null=True, verbose_name="Комментарии")

    # 📌 Декларация
    declaration_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Номер декларации")
    declaration_file = models.FileField(upload_to="declarations/", blank=True, null=True, verbose_name="Файл декларации (PDF)")

    # 📌 Анализы (может быть много файлов)
    analysis_files = models.FileField(upload_to="analysis_reports/", blank=True, null=True, verbose_name="Анализы (PDF)")

    # 📌 История услуг и квитанции
    service_date = models.DateField(blank=True, null=True, verbose_name="Дата услуги")
    service_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Код услуги")
    service_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Название услуги")
    service_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Цена услуги")
    receipt_file = models.FileField(upload_to="receipts/", blank=True, null=True, verbose_name="Квитанция (PDF)")

    # 📌 Пол
    gender = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=[("man", "Мужчина"), ("woman", "Женщина")],
        verbose_name="Пол"
    )

    # 📌 Соцсети
    instagram_username = models.CharField(max_length=100, blank=True, null=True, verbose_name="Instagram Ник")
    instagram_link = models.URLField(blank=True, null=True, verbose_name="Instagram Ссылка")
    instagram_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Instagram Телефон")

    telegram_username = models.CharField(max_length=100, blank=True, null=True, verbose_name="Telegram Ник")
    telegram_link = models.URLField(blank=True, null=True, verbose_name="Telegram Ссылка")
    telegram_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telegram Телефон")

    facebook_username = models.CharField(max_length=100, blank=True, null=True, verbose_name="Facebook Ник")
    facebook_link = models.URLField(blank=True, null=True, verbose_name="Facebook Ссылка")
    facebook_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Facebook Телефон")

    whatsapp_username = models.CharField(max_length=100, blank=True, null=True, verbose_name="WhatsApp Ник")
    whatsapp_link = models.URLField(blank=True, null=True, verbose_name="WhatsApp Ссылка")
    whatsapp_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="WhatsApp Телефон")

    viber_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Viber Телефон")

    # 📌 Адрес и геолокация
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="Страна")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    address = models.TextField(blank=True, null=True, verbose_name="Адрес")

    # 📌 Источник контакта
    source = models.CharField(max_length=255, blank=True, null=True, verbose_name="Источник (Instagram, реклама и т. д.)")
    referred_by = models.CharField(max_length=255, blank=True, null=True, verbose_name="Рекомендован кем-то")

    # 📌 Финансовая информация
    deal_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Сумма сделки")
    currency = models.CharField(max_length=10, blank=True, null=True, verbose_name="Валюта")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Оплаченная сумма")
    payment_status = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[("paid", "Оплачено"), ("pending", "Ожидание"), ("overdue", "Просрочено")],
        verbose_name="Статус оплаты"
    )

    # 📌 CRM-данные
    status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=[("lead", "Лид"), ("client", "Клиент"), ("closed", "Закрыто")],
        verbose_name="Статус клиента"
    )
    last_contact_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата последнего контакта")
    next_followup_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата следующего контакта")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="created_contacts", verbose_name="Создал")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="updated_contacts", verbose_name="Обновил")

    def __str__(self):
        return f"{self.fool_name}"

    class Meta:
        verbose_name = "Пациент"
        verbose_name_plural = "Пациенты"