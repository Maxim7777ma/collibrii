from django.contrib import admin
from .models import (
    ClinicBranch, ClinicRoom, Specialization, Doctor, Nurse, Pacient, 
    ServicePriceList, VisitRecord, VisitHistory, ServicePriceList
)




# 📌 Настройка админки для филиалов
@admin.register(ClinicBranch)
class ClinicBranchAdmin(admin.ModelAdmin):
    list_display = ("branch_name", "branch_address")
    search_fields = ("branch_name", "branch_address")
    list_filter = ("branch_name",)
    ordering = ("branch_name",)


# 📌 Настройка админки для кабинетов
@admin.register(ClinicRoom)
class ClinicRoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "branch")
    search_fields = ("room_number", "branch__branch_name")
    list_filter = ("branch",)


# 📌 Админка для услуг
@admin.register(ServicePriceList)
class ServicePriceListAdmin(admin.ModelAdmin):
    list_display = ("service_code", "service_name", "service_price")
    search_fields = ("service_code", "service_name")
    ordering = ("service_code",)


# 📌 Админка для врачей
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('fool_name', 'email', 'phone_number_1')
    search_fields = ( "room__room_number",)
    list_filter = ("branch", "specializations")
    ordering = ("fool_name",)


# 📌 Админка для медсестер
@admin.register(Nurse)
class NurseAdmin(admin.ModelAdmin):
    list_display = ('fool_name', 'email', 'phone_number')
    list_filter = ("branch",)
    ordering = ("fool_name",)


# 📌 Админка для пациентов
@admin.register(Pacient)
class PacientAdmin(admin.ModelAdmin):
    list_display = ("fool_name", "email", "phone_number_1", "birth_date", "attending_doctor", "medical_card_number")
    search_fields = ("fool_name",  "medical_card_number", "attending_doctor")
    list_filter = ("is_vip",)
    ordering = ("fool_name",)

    # 🔹 Автоматический расчет возраста
    def get_age(self, obj):
        return obj.age
    get_age.short_description = "Возраст"


# 📌 Инлайн-админка для записей на визит
class VisitRecordInline(admin.TabularInline):
    model = VisitRecord
    extra = 1
    show_change_link = True



# 📌 Админка для записей на визит
@admin.register(VisitRecord)
class VisitRecordAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "visit_date", "visit_time", "payment_status", "is_online")
    search_fields = ("patient__fool_name", "patient__fool_name", "doctor__fool_name", "doctor__fool_name")
    list_filter = ("payment_status", "is_online", "doctor")
    ordering = ("-visit_date",)

    # 🔹 Автоматически переносим в историю после оплаты
    def save_model(self, request, obj, form, change):
        """Перенос записи в VisitHistory и удаление из VisitRecord после полной оплаты"""
        obj.save()  # ✅ Сначала сохраняем VisitRecord, чтобы у него был ID
        form.save_m2m()  # ✅ Сохраняем ManyToMany связи (услуги)

  


# 📌 Админка для истории визитов
@admin.register(VisitHistory)
class VisitHistoryAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "visit_date", "total_price", "is_online")
    search_fields = ("patient__fool_name", "patient__fool_name", "doctor__first_name", "doctor__fool_name")
    list_filter = ("is_online",)
    ordering = ("-visit_date",)


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)




