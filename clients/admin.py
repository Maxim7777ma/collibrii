from django.contrib import admin
from .models import Client, CustomRow

# Регистрация модели Client
admin.site.register(Client)

# Админ-класс для CustomRow
class CustomRowAdmin(admin.ModelAdmin):
    list_display = ('name', 'table', 'manually_updated', 'last_updated', 'get_updated_by_users')
    list_filter = ('status', 'priority', 'updated_by', 'manually_updated')
    search_fields = ('name', 'instagram_username', 'phone_number')
    readonly_fields = ('last_updated',)
    autocomplete_fields = ['updated_by']  # Это позволит выбирать пользователя из списка
    def get_updated_by_users(self, obj):
        # Вернёт запятую, через которую перечислим всех юзеров
        return ", ".join([user.username for user in obj.updated_by.all()])
    get_updated_by_users.short_description = "Updated By"
# Удаление старой регистрации CustomRow, если она была
try:
    admin.site.unregister(CustomRow)
except admin.sites.NotRegistered:
    pass

# Регистрация CustomRow с использованием CustomRowAdmin
admin.site.register(CustomRow, CustomRowAdmin)
