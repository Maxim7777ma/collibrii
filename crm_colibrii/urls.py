"""
URL configuration for crm_colibrii project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


from django.shortcuts import render
from medicalCRM.views import (
    VisitListCreateView, NurseListView, ServiceListView, 
    DoctorListView, PatientListView,UpdateVisitView,BranchListView, RoomListView,FilteredVisitRecords,SpecializationListView,DoctorsBySpecializationAPIView
)
from medicalCRM import views

# Функция рендеринга страницы календаря
def calendar_view(request):
    return render(request, 'medicalCRM/calendar.html')
urlpatterns = [
    path('admin/', admin.site.urls),  # Админка
    path('login/', auth_views.LoginView.as_view(template_name='clients/login.html'), name='login'),  # Логин
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Логаут
    path('clients/', include('clients.urls')),  # Перенаправление в приложение "clients"
    path('analysis/', include('analysis.urls')),  # Приложение "analysis"
    path('', auth_views.LoginView.as_view(template_name='clients/first.html'), name='first'),  # Главная страница
    path('medicalCRM/', include('medicalCRM.urls')), 
    path('api/visits/<int:pk>/', UpdateVisitView.as_view(), name='update_visit'),
    path('api/visits/', VisitListCreateView.as_view(), name='visits'),
    path('api/nurses/', NurseListView.as_view(), name='nurses'),
    path('api/services/', ServiceListView.as_view(), name='services'),
    path("api/branches/", BranchListView.as_view(), name="branch_list"),
    path("api/rooms/", RoomListView.as_view(), name="room_list"),
    path('api/doctors/', DoctorListView.as_view(), name='doctors'),
    path('api/patients/', PatientListView.as_view(), name='patients'),
    path('api/filtered-visits/', FilteredVisitRecords.as_view(), name='filtered_visits'),  # Путь для фильтрации визитов
    path('api/specializations/', SpecializationListView.as_view(), name='specializations'),
    path('api/doctors-by-specialization/<int:specialization_id>/', DoctorsBySpecializationAPIView.as_view(), name='doctors-by-specialization'),
    path('api/get_filtered_visits/', views.get_filtered_visits, name='get_filtered_visits'),
    path('api/visit/', views.VisitRecordViewSet.as_view({'get': 'list'}), name='visit_record_list'),
    path('api/visit/create/', views.create_visit, name='create_visit'),
    path('api/visit/<int:visit_id>/update/', views.update_visit, name='update_visit'),
    path('api/visit/<int:visit_id>/delete/', views.DeleteVisitRecordView.as_view(), name='delete_visit'),

    path('calendar/', calendar_view, name='calendar'), 
    path('login', auth_views.LoginView.as_view(template_name='clients/login.html'), name='home'),  # Главная страница = логин
]