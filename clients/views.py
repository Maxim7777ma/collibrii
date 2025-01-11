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


@csrf_exempt
def update_status1(request, row_id):
    print(f"Received request to update status for row_id: {row_id}")
    if request.method == 'POST':
        status = request.POST.get('status')
        row = get_object_or_404(CustomRow, id=row_id)
        row.status = status
        row.save()
        return JsonResponse({'success': True})
    


@csrf_exempt
def update_contact1(request, row_id):
    print(f"Received request to update status for row_id: {row_id}")
    if request.method == 'POST':
        contact = request.POST.get('contact')
        row = get_object_or_404(CustomRow, id=row_id)
        row.contact = contact
        row.save()
        return JsonResponse({'success': True})
    
def table_rows(request, table_id):
    table = get_object_or_404(CustomTable, id=table_id)
    rows = CustomRow.objects.filter(table=table)
    duplicate_links = [row.instagram_link for row in rows if rows.filter(instagram_link=row.instagram_link).count() > 1]
    duplicate_phones = [row.phone_number for row in rows if rows.filter(phone_number=row.phone_number).count() > 1]
    return render(request, 'table_rows.html', {
        'table': table,
        'rows': rows,
        'duplicate_links': duplicate_links,
        'duplicate_phones': duplicate_phones,
    })

# Функция редактирования строки
def edit_row(request, table_id, row_id):
    table = get_object_or_404(CustomTable, id=table_id)
    row = get_object_or_404(CustomRow, id=row_id, table=table)

    if request.method == "POST":
        form = CustomRowForm(request.POST, instance=row)
        if form.is_valid():
            row = form.save(commit=False)
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
    # Получаем таблицу по ID
    table = get_object_or_404(CustomTable, id=table_id)

    # Получаем все строки для данной таблицы
    rows = CustomRow.objects.filter(table=table)

    # Поиск дубликатов по Instagram и телефону
    duplicates = rows.values('instagram_link', 'phone_number').annotate(count=Count('id')).filter(count__gt=1)
    duplicate_links = [item['instagram_link'] for item in duplicates]
    duplicate_phones = [item['phone_number'] for item in duplicates]

    # Передаём данные в шаблон
    return render(request, 'clients/custom_row_list.html', {
        'table': table,
        'rows': rows,
        'duplicate_links': duplicate_links,
        'duplicate_phones': duplicate_phones
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
    table = get_object_or_404(CustomTable, id=table_id)

    if request.method == "POST":
        form = CustomRowForm(request.POST)
        if form.is_valid():
            row = form.save(commit=False)
            row.table = table
            row.save()
            # Перенаправляем на список строк после сохранения
            return redirect('custom_row_list', table_id=table.id)
        else:
            print(form.errors)  # Логируем ошибки в консоль для диагностики
    else:
        form = CustomRowForm()

    last_values = {
        'deal_amount': '',
        'deal_amount_currency': 'UAH',
        'paid_amount': '',
        'paid_amount_currency': 'UAH',
        'expected_profit': '',
        'expected_profit_currency': 'UAH',
    }

    return render(request, 'clients/custom_row_form.html', {'form': form, 'table': table, 'last_values': last_values})


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


