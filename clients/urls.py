from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_dashboard, name='main_dashboard'), # Главная страница CRM
    path('clients/leads/', views.client_list_leads, name='client_list_leads'), # Лиды
    path('clients/clients/', views.client_list_clients, name='client_list_clients'), # Клиенты
    path('clients/customers/', views.client_list_customers, name='client_list_customers'), # Заказчики
    path('create/', views.client_create, name='client_create'), # Добавить клиента
    path('<int:pk>/edit/', views.client_edit, name='client_edit'), # Редактировать клиента
    path('logout/', views.logout_view, name='logout'), # Выход из системы
    path('update-status/<int:pk>/', views.update_status, name='update_status'), # Обновить статус
    path('delete-client/<int:pk>/', views.delete_client, name='delete_client'), # Удалить клиента
    path('update-contact/<int:pk>/', views.update_contact, name='update_contact'), # Обновить контакт
    path('clients/all/', views.client_list_all, name='client_list'), # Общий список клиентов
    path('check-duplicate-link/', views.check_duplicate_link, name='check_duplicate_link'),
    path('tables/', views.custom_table_list, name='custom_table_list'),  # Список таблиц
    path('tables/create/', views.custom_table_create, name='custom_table_create'),  # Создание таблицы
    path('tables/<int:table_id>/edit/', views.edit_table, name='custom_table_edit'),
    path('tables/<int:table_id>/delete/', views.delete_table, name='custom_table_delete'),
    path('tables/<int:table_id>/', views.custom_row_list, name='custom_row_list'),  # Просмотр строк в таблице
    path('tables/<int:table_id>/add/', views.add_row, name='add_row'), # Добавление строки в таблицу
    path('tables/<int:table_id>/edit/<int:row_id>/', views.edit_row, name='edit_row'),  # Редактировать строку
    path('tables/<int:table_id>/delete-row/<int:pk>/', views.delete_row, name='delete_row'),   # Удалить строку
    path('tables/update-status/<int:row_id>/', views.update_status, name='update_status'),
    path('tables/update-contact1/<int:pk>/', views.update_contact1, name='update_contact1'),
    path('tables/update-status1/<int:pk>/', views.update_status1, name='update_status1'),
    path('tables/update-priority/<int:pk>/', views.update_priority, name='update_priority'),
    path('tables/<int:table_id>/', views.table_rows, name='table_rows'),
    path('tables/filter-rows/<int:table_pk>/', views.filter_rows, name='filter_rows_all'),
    path('tables/reset_filter/<int:pk>/', views.reset_row_filter, name='reset_row_filter'),
    path('tables/update-field/<int:row_id>/', views.update_field, name='update_field'),
    path('tables/<int:table_pk>/upload-excel/', views.upload_excel, name='upload_excel'),
    path('tables/<int:table_pk>/resolve-duplicate/', views.resolve_duplicate, name='resolve_duplicate'),
]