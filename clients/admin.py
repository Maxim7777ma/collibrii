from django.contrib import admin
from .models import Client, CustomRow

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Permission

# Регистрация модели Client
admin.site.register(Client)

class CustomUserAdmin(UserAdmin):
    fieldsets = list(UserAdmin.fieldsets)  # Создаем копию, чтобы избежать изменений в оригинале
    custom_permissions_field = ('Дополнительные права', {'fields': ('user_permissions',)})

# Добавляем только если 'user_permissions' еще нет в fieldsets
    if not any('user_permissions' in field[1].get('fields', []) for field in fieldsets):
        fieldsets.append(custom_permissions_field)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

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
    
    def save_model(self, request, obj, form, change):
        """Принудительно устанавливаем manually_updated = False, если нет прав"""
        if not request.user.has_perm('clients.can_update_manually'):
            obj.manually_updated = False
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        """Ограничение полей в зависимости от прав"""
        readonly = list(self.readonly_fields)  # Список неизменяемых полей
        if not request.user.has_perm('clients.can_update_manually'):
            readonly.extend(['manually_updated', 'updated_by'])  # Делаем оба readonly
        return readonly

    def get_fields(self, request, obj=None):
        """Скрытие `updated_by`, если нет доступа к `manually_updated`"""
        fields = super().get_fields(request, obj)
        readonly = self.get_readonly_fields(request, obj)
        if 'manually_updated' in readonly:
            return [field for field in fields if field not in ('manually_updated', 'updated_by')]
    
        return fields
    
# Удаление старой регистрации CustomRow, если она была
try:
    admin.site.unregister(CustomRow)
except admin.sites.NotRegistered:
    pass

# Регистрация CustomRow с использованием CustomRowAdmin
admin.site.register(CustomRow, CustomRowAdmin)



