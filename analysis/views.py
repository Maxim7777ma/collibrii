
from clients.models import Client  # пример импорта модели
from django.shortcuts import render, get_object_or_404
from clients.models import CustomTable, CustomRow
from django.db.models import Count, Avg, Sum

from django.db.models import Count, Avg, Sum, Q
from django.http import JsonResponse


def analysis_dashboard(request):
    """Выводит список всех таблиц"""
    tables = CustomTable.objects.all()
    

    return render(request, 'analysis/dashboard.html', {'tables': tables})



 
def table_analysis(request, table_id):
    """Фильтрация данных и анализ по менеджерам"""
    table = get_object_or_404(CustomTable, id=table_id)
    rows = CustomRow.objects.filter(table=table)

    # Получаем уникальных менеджеров (убираем None)
    managers = rows.exclude(manager__isnull=True).values_list("manager", flat=True).distinct().order_by("manager")

    # Получаем параметры фильтрации из запроса
    filters = {
        "status": request.GET.get("status", ""),
        "contact": request.GET.get("contact", ""),
        "priority": request.GET.get("priority", ""),
        "manager": request.GET.get("manager", ""),
        "phone_number": request.GET.get("phone_number", ""),
        "min_deal": request.GET.get("min_deal", ""),
        "max_deal": request.GET.get("max_deal", ""),
        "deal_currency": request.GET.get("deal_currency", ""),
        "start_date": request.GET.get("start_date", ""),
        "end_date": request.GET.get("end_date", ""),
    }

    # Фильтрация данных
    query = Q()
    if filters["status"]:
        query &= Q(status=filters["status"])
    if filters["contact"]:
        query &= Q(contact=filters["contact"])
    if filters["priority"]:
        query &= Q(priority=filters["priority"])
    if filters["phone_number"]:
        query &= Q(phone_number__icontains=filters["phone_number"])
    if filters["manager"]:
        query &= Q(manager=filters["manager"])
    if filters["min_deal"]:
        query &= Q(deal_amount__gte=float(filters["min_deal"]))
    if filters["max_deal"]:
        query &= Q(deal_amount__lte=float(filters["max_deal"]))
    if filters["deal_currency"]:
        query &= Q(deal_amount_currency=filters["deal_currency"])
    if filters["start_date"]:
        query &= Q(record_date__gte=filters["start_date"])
    if filters["end_date"]:
        query &= Q(record_date__lte=filters["end_date"])

    # Получаем строки, соответствующие фильтру
    filtered_rows = rows.filter(query)

    # Флаг "нет данных"
    no_data = filtered_rows.count() == 0


    all_managers = rows.values("manager").annotate(
    total_clients=Count("id"),
    total_deal_amount=Sum("deal_amount")
        ).order_by("manager")

    # Подсчет общей статистики по менеджерам
    manager_stats_total = rows.values("manager").annotate(
    total_clients=Count("id"),
    total_deal_amount=Sum("deal_amount")
    ).order_by("manager")

    # Подготовка менеджеров с 0 значениями (чтобы все были в таблице)
    manager_stats_filtered = {m["manager"]: {"total_clients": 0, "total_deal_amount": 0} for m in all_managers}

    
# Заполняем только подходящие данные (игнорируем фильтр по менеджеру)
    for m in rows.filter(
        **{k: v for k, v in filters.items() if k != "manager" and v}  # Исключаем менеджера из фильтрации
    ).values("manager").annotate(
        total_clients=Count("id"),
        total_deal_amount=Sum("deal_amount")
    ):
        manager_stats_filtered[m["manager"]]["total_clients"] = m["total_clients"]
        manager_stats_filtered[m["manager"]]["total_deal_amount"] = m["total_deal_amount"]

    # Преобразуем обратно в список, чтобы передать в шаблон
    manager_stats_filtered = [
        {"manager": manager, "total_clients": data["total_clients"], "total_deal_amount": data["total_deal_amount"]}
        for manager, data in manager_stats_filtered.items()
    ]         

    # Подсчет статистики по отфильтрованным данным
    filtered_manager_stats = filtered_rows.values("manager").annotate(
        total_clients=Count("id"),
        total_deal_amount=Sum("deal_amount")
    ).order_by("manager")

    # Найти выбранного менеджера в отфильтрованных данных
    selected_manager_stats = None
    if filters["manager"]:
        selected_manager_stats = next(
            (m for m in filtered_manager_stats if m["manager"] == filters["manager"]), None
        )

    return render(request, "analysis/table_analysis.html", {
        "table": table,
        "rows": rows,
        "filtered_rows": filtered_rows,
        "manager_stats_filtered": manager_stats_filtered,  # Фильтрованные данные
        
        "filtered_manager_stats": filtered_manager_stats,  # Фильтрованная статистика
        
        "filters": filters,
        "no_data": no_data,
        "managers": managers,  # Передаем список менеджеров
        "manager_stats_filtered": manager_stats_filtered,  # Теперь все менеджеры с 0 у кого нет клиентов
        "manager_stats_total": manager_stats_total,  # Общая статистика
        "selected_manager": filters["manager"],  # Выбранный менеджер
        "filtered_rows": filtered_rows,
        
        "manager_stats_total": all_managers,  # Общая статистика по менеджерам
        "selected_manager": filters.get("manager", ""),  # Выбранный менеджер
    })


def update_row(request, row_id):
    """Обновление данных записи через AJAX"""
    if request.method == "POST":
        row = get_object_or_404(CustomRow, id=row_id)
        field = request.POST.get('field')
        value = request.POST.get('value')

        if field in ['status', 'contact', 'priority', 'phone_number', 'deal_amount', 'deal_amount_currency']:
            setattr(row, field, value)
            row.save()
            return JsonResponse({'success': True})

    return JsonResponse({'success': False})
