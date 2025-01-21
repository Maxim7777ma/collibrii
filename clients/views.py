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


from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from .models import Client, CustomTable


from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from .models import CustomRow, CustomTable
from datetime import datetime

from django.shortcuts import redirect

@login_required
def reset_row_filter(request, pk):
    # Перенаправляем на страницу фильтрации без параметров
    return redirect('custom_row_filter', pk=pk)


@login_required
def custom_row_filter(request, pk):
    # Получаем таблицу по pk
    table = get_object_or_404(CustomTable, pk=pk)

    # Если метод POST, извлекаем параметры фильтрации
    filters = {
        'name': request.POST.get('name', '').strip(),
        'status': request.POST.get('status', '').strip(),
        'manager': request.POST.get('manager', '').strip(),
        'contact': request.POST.get('contact', '').strip(),
        'min_deal_amount': request.POST.get('min_deal_amount', '').strip(),
        'max_deal_amount': request.POST.get('max_deal_amount', '').strip(),
        'start_date': request.POST.get('start_date', '').strip(),
        'end_date': request.POST.get('end_date', '').strip(),
        'priority': request.POST.get('priority', '').strip(),
        'country': request.POST.get('country', '').strip(),
        'city': request.POST.get('city', '').strip(),
        'phone_number': request.POST.get('phone_number', '').strip(),
        'email': request.POST.get('email', '').strip(),
        'instagram_username': request.POST.get('instagram_username', '').strip(),
    }

    # Базовый запрос
    rows = CustomRow.objects.filter(table=table)

    # Применяем фильтры
    if filters['name']:
        rows = rows.filter(name__icontains=filters['name'])
    if filters['status']:
        rows = rows.filter(status=filters['status'])
    if filters['manager']:
        rows = rows.filter(manager__icontains=filters['manager'])
    if filters['contact']:
        rows = rows.filter(contact=filters['contact'])
    if filters['min_deal_amount']:
        try:
            rows = rows.filter(deal_amount__gte=float(filters['min_deal_amount']))
        except ValueError:
            pass
    if filters['max_deal_amount']:
        try:
            rows = rows.filter(deal_amount__lte=float(filters['max_deal_amount']))
        except ValueError:
            pass
    if filters['start_date']:
        rows = rows.filter(record_date__gte=filters['start_date'])
    if filters['end_date']:
        rows = rows.filter(record_date__lte=filters['end_date'])
    if filters['priority']:
        rows = rows.filter(priority=filters['priority'])
    if filters['country']:
        rows = rows.filter(country__icontains=filters['country'])
    if filters['city']:
        rows = rows.filter(city__icontains=filters['city'])
    if filters['phone_number']:
        rows = rows.filter(phone_number__icontains=filters['phone_number'])
    if filters['instagram_username']:
        rows = rows.filter(instagram_username__icontains=filters['instagram_username'])
    if filters['email']:
        rows = rows.filter(email__icontains=filters['email'])    
    

    # Поиск дубликатов
    duplicates = rows.values('instagram_link').annotate(count=Count('instagram_link')).filter(count__gt=1)
    duplicate_links = [item['instagram_link'] for item in duplicates]

    # Уникальные менеджеры
    managers = CustomRow.objects.filter(table=table).values_list('manager', flat=True).distinct()

    # Передача данных в шаблон
    return render(request, 'clients/custom_row_list.html', {
        'rows': rows,
        'duplicate_links': duplicate_links,
        'filters': filters,
        'managers': managers,
        'table': table,
    })


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
def edit_row(request, table_id, row_id):
    if not request.user.is_authenticated:
        return redirect('login')  # Перенаправление на страницу входа

    table = get_object_or_404(CustomTable, id=table_id)
    row = get_object_or_404(CustomRow, id=row_id, table=table)

    if request.method == "POST":
        form = CustomRowForm(request.POST, instance=row)
        if form.is_valid():
            row = form.save(commit=False)# Устанавливаем текущего пользователя
            row.updated_by = request.user 
            if form.cleaned_data['deal_amount'] is not None:
                row.deal_amount = form.cleaned_data['deal_amount']
            if form.cleaned_data['deal_amount_currency']:
                row.deal_amount_currency = form.cleaned_data['deal_amount_currency']

            if form.cleaned_data['paid_amount'] is not None:
                row.paid_amount = form.cleaned_data['paid_amount']
            if form.cleaned_data['paid_amount_currency']:
                row.paid_amount_currency = form.cleaned_data['paid_amount_currency']

            if form.cleaned_data['expected_profit'] is not None:
                row.expected_profit = form.cleaned_data['expected_profit']
            if form.cleaned_data['expected_profit_currency']:
                row.expected_profit_currency = form.cleaned_data['expected_profit_currency']
            row.contact = form.cleaned_data['contact']
            row.change_status_contact = form.cleaned_data['change_status_contact']
            row.save()
            return redirect('custom_row_list', table_id=table.id)
    else:
        initial_data = {
            'deal_amount': row.deal_amount if row.deal_amount else '',
            'deal_amount_currency': row.deal_amount_currency if row.deal_amount_currency else 'UAH',
            'paid_amount': row.paid_amount if row.paid_amount else '',
            'paid_amount_currency': row.paid_amount_currency if row.paid_amount_currency else 'UAH',
            'expected_profit': row.expected_profit if row.expected_profit else '',
            'expected_profit_currency': row.expected_profit_currency if row.expected_profit_currency else 'UAH',
            'contact': row.contact,
            'change_status_contact': row.change_status_contact,  # Предполагаем, что это поле должно быть заполнено текущим контактом
        }
        form = CustomRowForm(instance=row, initial=initial_data)

    last_values = {
        'deal_amount': row.deal_amount,
        'deal_amount_currency': row.deal_amount_currency,
        'paid_amount': row.paid_amount,
        'paid_amount_currency': row.paid_amount_currency,
        'expected_profit': row.expected_profit,
        'expected_profit_currency': row.expected_profit_currency,
        'change_status_contact': row.change_status_contact, 
    }

    return render(request, 'clients/custom_row_form.html', {'form': form, 'table': table, 'last_values': last_values})


# Функция удаления строки
def delete_row(request, table_id, row_id):
    table = get_object_or_404(CustomTable, id=table_id)
    row = get_object_or_404(CustomRow, id=row_id, table=table)

    if request.method == "POST":
        row.delete()
        return redirect('custom_row_list', table_id=table.id)

    return render(request, 'clients/confirm_delete.html', {'row': row, 'table': table})

# === Список строк в таблице ===
def custom_row_list(request, table_id):
    table = get_object_or_404(CustomTable, id=table_id)
    rows = CustomRow.objects.filter(table=table)

    # Поиск дубликатов по Instagram и телефону
    duplicate_usernames = rows.values('instagram_username').annotate(count=models.Count('id')).filter(count__gt=1)
    duplicate_usernames = [item['instagram_username'] for item in duplicate_usernames]

    duplicate_phones = rows.values('phone_number').annotate(count=models.Count('id')).filter(count__gt=1)
    duplicate_phones = [item['phone_number'] for item in duplicate_phones]

    return render(request, 'clients/custom_row_list.html', {
        'table': table,
        'rows': rows,
        'duplicate_usernames': duplicate_usernames,
        'duplicate_phones': duplicate_phones,
    })



# === Создание новой таблицы ===
def custom_table_create(request):
    if request.method == "POST":
        form = CustomTableForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('custom_table_list')  # Перенаправление на список таблиц
    else:
        form = CustomTableForm()
    return render(request, 'clients/create_table.html', {'form': form})  # Исправлен путь к шаблону


# === Список всех таблиц ===
def custom_table_list(request):
    tables = CustomTable.objects.all()
    return render(request, 'clients/table_list.html', {'tables': tables})  # Исправлен путь к шаблону


# === Добавление строки в таблицу ===
def add_row(request, table_id):
    """
    Функция для добавления строки в таблицу.
    """
    table = get_object_or_404(CustomTable, id=table_id)

    if request.method == "POST":
        form = CustomRowForm(request.POST)
        if form.is_valid():
            # Сохраняем данные из формы, но без сохранения в БД
            row = form.save(commit=False)
            row.table = table  # Привязываем строку к таблице
            row.country = form.cleaned_data.get('country')  # Сохраняем введённое значение страны
            row.save()  # Сохраняем строку в БД
            return redirect('custom_row_list', table_id=table.id)
        else:
            # Логирование ошибок для диагностики
            print(form.errors)
    else:
        # Инициализация формы для GET-запроса
        form = CustomRowForm()

    # Начальные значения для валют и сумм
    last_values = {
        'deal_amount': '',
        'deal_amount_currency': 'UAH',
        'paid_amount': '',
        'paid_amount_currency': 'UAH',
        'expected_profit': '',
        'expected_profit_currency': 'UAH',
    }

    # Рендеринг шаблона с передачей формы и начальных значений
    return render(
        request, 
        'clients/custom_row_form.html', 
        {
            'form': form,
            'table': table,
            'last_values': last_values
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



