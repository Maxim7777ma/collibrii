import json
from django.shortcuts import render, get_object_or_404, redirect
from .models import Client
from .forms import ClientForm
from django.db import models
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Client
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Client
from django.db.models import Count
from .models import CustomTable, CustomRow
from .forms import CustomRowForm
from .forms import CustomTableForm
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from .forms import FIELD_TRANSLATIONS
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from .models import Client, CustomTable
from django.contrib.auth.models import User

from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from .models import CustomRow, CustomTable
from datetime import datetime

from django.shortcuts import redirect
from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import CustomTable
from .forms import CustomTableForm
import json
from django import template


register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return "-"  # Если словарь отсутствует, вернуть дефолтное значение
    return dictionary.get(key, "-")  # Вернуть значение по ключу или "-"

@csrf_exempt
def update_field(request, row_id):
    """
    Универсальный API для обновления `contact`, `status`, `priority`, `change_status_contact`.
    Если `contact` == `change_status_contact`, то `status` меняется на `client`.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            field = data.get("field")  # Например, 'contact', 'status' и т. д.
            new_value = data.get("value")  # Новое значение

            row = CustomRow.objects.get(id=row_id)
            setattr(row, field, new_value)  # Устанавливаем новое значение

            auto_status_change = False  # Флаг для авто-изменения статуса

            # Если `contact` и `change_status_contact` совпадают, статус → client
            if field in ["contact", "change_status_contact"]:
                if row.contact and row.change_status_contact and row.contact == row.change_status_contact:
                    row.status = "client"
                    auto_status_change = True  # Сообщим фронту

            row.save()

            return JsonResponse({
                "success": True,
                "message": f"Поле {field} обновлено!",
                "auto_status_change": auto_status_change
            })
        except CustomRow.DoesNotExist:
            return JsonResponse({"success": False, "error": "Строка не найдена!"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Некорректный запрос!"}, status=400)

def get_updated_by_usernames(self):
    """
    Преобразует ID пользователей из JSON в список usernames.
    """
    if not self.additional_data:
        return []

    try:
        data = json.loads(self.additional_data)
        user_ids = data.get('updated_by', [])

        # Если данные были сохранены как строка, конвертируем в int
        if isinstance(user_ids, str):
            user_ids = [int(user_ids)]
        elif isinstance(user_ids, list):
            user_ids = [int(uid) for uid in user_ids]

        # Получаем пользователей по ID и возвращаем их usernames
        return list(User.objects.filter(id__in=user_ids).values_list('username', flat=True))

    except (json.JSONDecodeError, ValueError):
        return []

def edit_table(request, table_id):
    """
    Редактирование таблицы.
    """
    table = get_object_or_404(CustomTable, id=table_id)

    if request.method == "POST":
        form = CustomTableForm(request.POST, instance=table)
        if form.is_valid():
            # Обновляем поля таблицы
            table = form.save(commit=False)
            # Преобразуем видимые поля в формат списка словарей с ключом "name"
            table.visible_fields = [
                {"name": field} if isinstance(field, str) else field
                for field in form.cleaned_data.get('visible_fields', [])
            ]
            table.save()
            messages.success(request, "Таблиця успішно відредагована.")
            return redirect('custom_table_list')
    else:
        # Декодируем `visible_fields` из JSON (если необходимо)
        visible_fields = table.visible_fields
        if isinstance(visible_fields, str):
            try:
                visible_fields = json.loads(visible_fields)
            except json.JSONDecodeError:
                visible_fields = []

        # Преобразуем данные в список строк для инициализации формы
        initial_visible_fields = [field["name"] for field in visible_fields if isinstance(field, dict)]
        form = CustomTableForm(instance=table, initial={"visible_fields": initial_visible_fields})

    return render(request, 'clients/edit_table.html', {'form': form, 'table': table})

def delete_table(request, table_id):
    """
    Удаление таблицы.
    """
    table = get_object_or_404(CustomTable, id=table_id)

    if request.method == "POST":
        table.delete()
        messages.success(request, "Таблицу успешно удалено.")
        return redirect('custom_table_list')

    return redirect('custom_table_list')


@login_required
def reset_row_filter(request, pk):
    # Перенаправляем на страницу фильтрации без параметров
    return redirect('custom_row_filter', pk=pk)


import logging

logger = logging.getLogger(__name__)

def filter_rows(request, table_pk):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            table = get_object_or_404(CustomTable, pk=table_pk)
            rows = CustomRow.objects.filter(table=table)

            for field, value in data.items():
                if value:
                    rows = rows.filter(**{f"{field}__icontains": value})

            filtered_data = []
            for row in rows:
                row_data = {"pk": row.pk, "fields": {}}

                for field in table.visible_fields:
                    field_name = field["name"]
                    field_value = getattr(row, field_name, "-")

                    if isinstance(field_value, models.Manager):
                        field_value = list(field_value.values_list('id', flat=True))

                    row_data["fields"][field_name] = field_value

                filtered_data.append(row_data)

            return JsonResponse({"success": True, "data": filtered_data})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Некорректный JSON"}, status=400)
        except Exception as e:
            print("Ошибка в filter_rows:", str(e))  # Лог ошибки
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Некорректный запрос!"}, status=400)

@csrf_exempt
@login_required
def update_priority(request, pk):
    if request.method == 'POST':
        try:
            row = CustomRow.objects.get(pk=pk)
            data = json.loads(request.body)
            priority = data.get('priority')

            if priority in ['low', 'medium', 'high']:
                row.priority = priority
                row.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid priority value'})
        except CustomRow.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Row not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def update_status1(request, pk):
    """
    Обновление статуса существующей строки в таблице.
    """
    if request.method == 'POST':
        try:
            # Извлечение данных из тела запроса
            data = json.loads(request.body)
            new_status = data.get('status')

            if not new_status:
                return JsonResponse({'error': 'Новое значение статуса не указано.'}, status=400)

            # Поиск строки по pk
            row = get_object_or_404(CustomRow, pk=pk)

            # Обновляем поле status
            row.status = new_status
            row.save()

            # Возвращаем успешный ответ с данными обновлённой строки
            return JsonResponse({
                'success': True,
                'message': 'Статус успешно обновлён!',
                'updated_row': {
                    'id': row.id,
                    'table_id': row.table_id,
                    'status': row.status,
                }
            })

        except Exception as e:
            return JsonResponse({'error': f'Неожиданная ошибка: {str(e)}'}, status=500)

    # Обработка некорректного метода
    return JsonResponse({'error': 'Метод не поддерживается. Используйте POST.'}, status=405)

@csrf_exempt
def update_contact1(request, pk):
    """
    Обновление существующей строки в таблице: редактирование поля contact.
    """
    if request.method == 'POST':
        try:
            # Извлечение данных из тела запроса
            data = json.loads(request.body)
            new_contact = data.get('contact')

            if not new_contact:
                return JsonResponse({'error': 'Новое значение контакта не указано.'}, status=400)

            # Поиск строки по pk
            row = get_object_or_404(CustomRow, pk=pk)

            # Проверяем, изменилось ли значение
            if row.contact == new_contact:
                return JsonResponse({'warning': 'Значение контакта совпадает с текущим.'}, status=200)

            # Обновляем поле contact
            row.contact = new_contact

            # Логика изменения статуса
            

            row.save()

            # Возвращаем успешный ответ с данными обновлённой строки
            return JsonResponse({
                'success': True,
                'message': 'Контакт успешно обновлён!',
                'updated_row': {
                    'id': row.id,
                    'table_id': row.table_id,
                    'contact': row.contact,
                    'status': row.status,
                }
            })

        except Exception as e:
            return JsonResponse({'error': f'Неожиданная ошибка: {str(e)}'}, status=500)

    # Обработка некорректного метода
    return JsonResponse({'error': 'Метод не поддерживается. Используйте POST.'}, status=405)
    
def table_rows(request, table_id):
    table = get_object_or_404(CustomTable, id=table_id)
    rows = CustomRow.objects.filter(table=table)
    
    # Поиск дубликатов по никнейму Instagram
    duplicate_usernames = rows.values('instagram_username').annotate(count=models.Count('id')).filter(count__gt=1)
    duplicate_usernames = [item['instagram_username'] for item in duplicate_usernames]

    # Поиск дубликатов по телефону
    duplicate_phones = rows.values('phone_number').annotate(count=models.Count('id')).filter(count__gt=1)
    duplicate_phones = [item['phone_number'] for item in duplicate_phones]

    return render(request, 'table_rows.html', {
        'table': table,
        'rows': rows,
        'duplicate_usernames': duplicate_usernames,
        'duplicate_phones': duplicate_phones,
    })

# Функция редактирования строки
@login_required
def edit_row(request, table_id, row_id):
    """
    Функция для редактирования строки таблицы с учётом динамических полей.
    """
    # Получаем таблицу и строку по ID
    table = get_object_or_404(CustomTable, id=table_id)
    row = get_object_or_404(CustomRow, id=row_id, table=table)

    if request.method == "POST":
        if not request.user.is_authenticated:
            raise PermissionDenied("Вы должны быть авторизованы для выполнения этого действия.")
        
        # Передаём таблицу в форму для обработки динамических полей
        form = CustomRowForm(request.POST, table=table, instance=row, user=request.user)
        if form.is_valid():
            row = form.save(commit=False, user=request.user) # Сохраняем объект без коммита
            row.save()  # Сохраняем строку в базе данных
            return redirect('custom_row_list', table_id=table.id)
        else:
            # Логирование ошибок для диагностики
            print("Ошибки формы:", form.errors)
            print("Form errors:", form.errors)
    else:
        # Передаём текущую строку и таблицу в форму
        form = CustomRowForm(table=table, instance=row, user=request.user)

    return render(
        request, 
        'clients/custom_row_form.html', 
        {'form': form, 'table': table, 'row': row}
    )
def create_table(request):
    """
    Представление для создания новой таблицы.
    """
    # Поля, которые нужно исключить
    exclude_fields = ['deal_amount_currency', 'paid_amount_currency', 'expected_profit_currency']

    if request.method == "POST":
        # Инициализация формы с POST-данными
        form = CustomTableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)

            # Получаем видимые поля из формы
            visible_fields = form.cleaned_data['visible_fields']

            # Исключаем ненужные поля (например, связанные с валютами)
            filtered_fields = [
                {"name": field} for field in visible_fields if field not in exclude_fields
            ]

            # Сохраняем видимые поля в JSON-формате
            table.visible_fields = json.dumps(filtered_fields)
            table.save()

            return redirect('custom_table_list')  # Перенаправляем на список таблиц
    else:
        # Инициализация формы
        form = CustomTableForm()

    return render(request, 'clients/create_table.html', {'form': form})
# Функция удаления строки
def delete_row(request, table_id, row_id):
    table = get_object_or_404(CustomTable, id=table_id)
    row = get_object_or_404(CustomRow, id=row_id, table=table)

    if request.method == "POST":
        # Удаляем строку
        row.delete()
        return redirect('custom_row_list', table_id=table.id)

    # Если запрос не POST, показываем страницу подтверждения
    return render(request, 'clients/confirm_delete.html', {'row': row, 'table': table})

# Функция удаления строки
@csrf_exempt 
def delete_row(request, table_id, pk):
    # Получаем таблицу и строку по переданным ключам
    table = get_object_or_404(CustomTable, id=table_id)
    row = get_object_or_404(CustomRow, pk=pk, table=table)

    if request.method == "POST":
        row.delete()
        return redirect('custom_row_list', table_id=table.id)

    return render(request, 'clients/confirm_delete.html', {'row': row, 'table': table})

from collections import Counter

from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import CustomTable, CustomRow
import json

def custom_row_list(request, table_id):
    """
    Отображение строк таблицы.
    """
    # Получаем таблицу
    table = get_object_or_404(CustomTable, id=table_id)

    # Загружаем видимые поля
    visible_fields = table.visible_fields or []
    select_fields = ["contact", "status", "priority", "change_status_contact"]
    allowed_fields = [field["name"] for field in visible_fields if field["name"] in select_fields]
     # Определяем возможные варианты значений для select (если есть choices)
    choices = {}
    for field in allowed_fields:
        choices[field] = list(CustomRow.objects.values_list(field, flat=True).distinct())


    # Если visible_fields сохранены как JSON, декодируем их
    if isinstance(visible_fields, str):
        try:
            visible_fields = json.loads(visible_fields)
        except json.JSONDecodeError:
            visible_fields = []  # Если данные некорректны, задаем пустой список

    # Загружаем строки таблицы
    rows = CustomRow.objects.filter(table=table)

    # Декодируем additional_data для каждой строки
    for row in rows:
        if isinstance(row.additional_data, str):
            try:
                row.additional_data = json.loads(row.additional_data)
            except json.JSONDecodeError:
                row.additional_data = {}

    # Поиск дубликатов
    # Поиск дубликатов ТОЛЬКО в пределах текущей таблицы
    # Собираем все значения `instagram_username` и `phone_number` из additional_data
    instagram_usernames = []
    phone_numbers = []

    for row in rows:
        instagram_usernames.append(row.additional_data.get('instagram_username'))
        phone_numbers.append(row.additional_data.get('phone_number'))

    # Убираем пустые значения и считаем дубликаты
    duplicate_usernames = [key for key, count in Counter(filter(None, instagram_usernames)).items() if count > 1]
    duplicate_phones = [key for key, count in Counter(filter(None, phone_numbers)).items() if count > 1]

    if isinstance(table.visible_fields, str):
        try:
            table.visible_fields = json.loads(table.visible_fields)
        except json.JSONDecodeError:
            table.visible_fields = []

    visible_fields = [
        {"name": field["name"], "label": FIELD_TRANSLATIONS.get(field["name"], field["name"])}
        for field in table.visible_fields
    ]    

    # Обрабатываем additional_data для каждой строки
    for row in rows:
        if isinstance(row.additional_data, str):
            try:
                additional_data = json.loads(row.additional_data)
            except json.JSONDecodeError:
                additional_data = {}
        else:
            additional_data = row.additional_data or {}

        # Получаем список ID пользователей из additional_data
        updated_by_ids = additional_data.get("updated_by", [])

        if isinstance(updated_by_ids, str):  # Если ID записаны как строка (например, "['1', '2']")
            updated_by_ids = updated_by_ids.strip("[]").replace("'", "").split(", ")

        updated_by_ids = [int(uid) for uid in updated_by_ids if str(uid).isdigit()]

        # Находим пользователей по ID и преобразуем в список никнеймов
        users = User.objects.filter(id__in=updated_by_ids).values_list("username", flat=True)
        row.updated_by_names = ", ".join(users) if users else "-"
    

    return render(request, 'clients/custom_row_list.html', {
        'table': table,
        'rows': rows,
        'visible_fields': visible_fields,  # Передаем список видимых полей
        'duplicate_usernames': list(duplicate_usernames),
        'duplicate_phones': list(duplicate_phones),
        'field_translations': FIELD_TRANSLATIONS, 
        'allowed_fields': allowed_fields,  # ✅ Передаем разрешенные поля
        'choices': choices,  # ✅ Передаем в шаблон возможные значения для select
    })


# === Создание новой таблицы ===
def custom_table_create(request):
    if request.method == "POST":
        form = CustomTableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)

            # Сохраняем видимые поля в виде JSON
            table.visible_fields = [{"name": field} for field in form.cleaned_data['visible_fields']]
            table.save()
            return redirect('custom_table_list')
    else:
        form = CustomTableForm()
    return render(request, 'clients/create_table.html', {'form': form})

# === Список всех таблиц ===
def custom_table_list(request):
    tables = CustomTable.objects.all()
    return render(request, 'clients/table_list.html', {'tables': tables})  # Исправлен путь к шаблону


def add_row(request, table_id):
    """
    Функция для добавления строки в таблицу.
    """
    # Получаем таблицу по ID
    table = get_object_or_404(CustomTable, id=table_id)
    
    if request.method == "POST":
        # Передаём таблицу в форму
        form = CustomRowForm(request.POST, table=table, user=request.user)
        if form.is_valid():
            # Сохраняем данные из формы
            row = form.save(commit=False, user=request.user, table=table)
            row.table = table  # Привязываем строку к таблице
            if not row.table:  # ✅ Если `table` не установлена — устанавливаем явно
                row.table = table  
            row.save()  # Сохраняем строку в БД
            row.manually_updated = form.cleaned_data.get('manually_updated', False)
            return redirect('custom_row_list', table_id=table.id)
        else:
            # Логирование ошибок для диагностики
            print(form.errors)
            print("Form errors:", form.errors)
    else:
        # Создаём пустую форму, передавая таблицу
        form = CustomRowForm(table=table, user=request.user)

    # Рендеринг шаблона с формой
    return render(
        request,
        'clients/custom_row_form.html',
        {
            'form': form,
            'table': table
        }
    )


# === Проверка дубликатов по ссылке ===
@csrf_exempt
def check_duplicate_link(request):
    if request.method == "POST":
        link = request.POST.get('link')  # Получаем ссылку из формы
        duplicate = Client.objects.filter(instagram_link=link).exists()  # Проверяем наличие дубликата
        return JsonResponse({'is_duplicate': duplicate})
    return JsonResponse({'error': 'Неверный запрос'}, status=400)


# === Общий список клиентов ===
def client_list_all(request):
    clients = Client.objects.all()
    managers = Client.objects.values_list('manager', flat=True).distinct()
    return render(request, 'clients/client_list.html', {
        'clients': clients,
        'managers': managers
    })


# === Список лидов ===
def client_list_leads(request):
    clients = Client.objects.filter(status='lead')

    # Поиск дубликатов по ссылке
    duplicates = clients.values('instagram_link').annotate(count=Count('instagram_link')).filter(count__gt=1)
    duplicate_links = [item['instagram_link'] for item in duplicates]

    managers = Client.objects.values_list('manager', flat=True).distinct()
    return render(request, 'clients/client_list.html', {
        'clients': clients,
        'managers': managers,
        'duplicate_links': duplicate_links
    })


# === Список клиентов ===
def client_list_clients(request):
    clients = Client.objects.filter(status='client')

    # Поиск дубликатов по ссылке
    duplicates = clients.values('instagram_link').annotate(count=Count('instagram_link')).filter(count__gt=1)
    duplicate_links = [item['instagram_link'] for item in duplicates]

    managers = Client.objects.values_list('manager', flat=True).distinct()
    return render(request, 'clients/client_list.html', {
        'clients': clients,
        'managers': managers,
        'duplicate_links': duplicate_links
    })


# === Список заказчиков ===
def client_list_customers(request):
    clients = Client.objects.filter(status='customer')

    # Поиск дубликатов по ссылке
    duplicates = clients.values('instagram_link').annotate(count=Count('instagram_link')).filter(count__gt=1)
    duplicate_links = [item['instagram_link'] for item in duplicates]

    managers = Client.objects.values_list('manager', flat=True).distinct()
    return render(request, 'clients/client_list.html', {
        'clients': clients,
        'managers': managers,
        'duplicate_links': duplicate_links
    })


@csrf_exempt
def update_status(request, pk):
    if request.method == "POST":
        try:
            client = Client.objects.get(pk=pk)
            status = request.POST.get('status')
            client.status = status
            client.save()
            return JsonResponse({'success': True})
        except Client.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Клиент не найден'})
    return JsonResponse({'success': False, 'error': 'Неверный запрос'})

@csrf_exempt
def update_contact(request, row_id):
    if request.method == "POST":
        contact = request.POST.get('contact')
        row = get_object_or_404(CustomRow, id=row_id)

        row.contact = contact

        # Логика изменения статуса
        if contact == 'contact_1':
            row.status = 'client'
        else:
            row.status = 'lead'

        row.save()

        return JsonResponse({'success': True, 'status': row.status})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
def main_dashboard(request):
    return render(request, 'clients/index.html')

# Функция для выхода из системы
def logout_view(request):
    logout(request)
    return redirect('login')

# Список клиентов с поиском и фильтрацией
@login_required
def client_list_all(request):
    # Получаем параметры фильтрации
    query = request.GET.get('q')
    link_query = request.GET.get('link')
    status_filter = request.GET.get('status')  # Фильтр по статусу
    manager_filter = request.GET.get('manager')  # Фильтр по менеджеру

    # Начальный запрос - все клиенты
    clients = Client.objects.all()

    # Применяем фильтры
    if query:
        clients = clients.filter(name__icontains=query)
    if link_query:
        clients = clients.filter(instagram_link__icontains=link_query)
    if status_filter:
        clients = clients.filter(status=status_filter)  # Фильтр по статусу
    if manager_filter:
        clients = clients.filter(manager__icontains=manager_filter)

    # Поиск дубликатов по ссылке
    duplicates = clients.values('instagram_link').annotate(count=models.Count('instagram_link')).filter(count__gt=1)
    duplicate_links = [item['instagram_link'] for item in duplicates]

    # Передаём данные в шаблон
    managers = Client.objects.values_list('manager', flat=True).distinct()
    return render(request, 'clients/client_list.html', {
        'clients': clients,
        'duplicate_links': duplicate_links,
        'managers': managers
    })

@login_required
def client_create(request):
    if request.method == "POST":
        form = ClientForm(request.POST)

        # Проверка дубликата ссылки
        link = request.POST.get('instagram_link')
        confirm_duplicate = request.POST.get('confirm_duplicate')

        if Client.objects.filter(instagram_link=link).exists() and confirm_duplicate != 'yes':
            # Если дубликат и подтверждения нет — вернём форму с предупреждением
            return render(request, 'clients/client_form.html', {'form': form})

        # Если подтверждено или нет дубликата — сохраняем клиента
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, 'clients/client_form.html', {'form': form})


@login_required
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/client_form.html', {'form': form})


@csrf_exempt
def delete_client(request, pk):
    if request.method == "POST":
        client = get_object_or_404(Client, pk=pk)  # Находим клиента по ID
        client.delete()  # Удаляем клиента из базы данных
        return HttpResponse(status=200)  # Возвращаем статус успеха
    return HttpResponse(status=400)  # Если метод не POST

@login_required
def main_dashboard(request):
    total_clients = Client.objects.count()
    leads = Client.objects.filter(status='lead').count()
    clients = Client.objects.filter(status='client').count()
    customers = Client.objects.filter(status='customer').count()
    return render(request, 'clients/index.html', {
        'total_clients': total_clients,
        'leads': leads,
        'clients': clients,
        'customers': customers,
    })