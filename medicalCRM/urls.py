from django.urls import path
from django.shortcuts import render

from .views import (
    VisitListCreateView, NurseListView, ServiceListView, 
    DoctorListView, PatientListView, DeleteVisitRecordView,
    BranchListView, RoomListView,ClinicRoomViewSet,UpdateVisitView,FilteredVisitRecords,SpecializationListView,DoctorsBySpecializationAPIView
)

from . import views





# 📌 Функция для рендеринга календаря
def calendar_view(request):
    return render(request, 'medicalCRM/calendar.html')

# 📌 Определение маршрутов API
urlpatterns = [
    path('api/visits/', VisitListCreateView.as_view(), name='visits'),
    path('api/nurses/', NurseListView.as_view(), name='nurses'),
    path('api/services/', ServiceListView.as_view(), name='services'),
    path('api/doctors/', DoctorListView.as_view(), name='doctors'),
    path('api/doctors-by-specialization/<int:specialization_id>/', DoctorsBySpecializationAPIView.as_view(), name='doctors-by-specialization'),
    path('api/patients/', PatientListView.as_view(), name='patients'),
    path('calendar/', calendar_view, name='calendar'),  
    path('delete_visit/<int:record_id>/', DeleteVisitRecordView.as_view(), name='delete_visit_record'),
    path('create-visit_start/', views.index, name="index"),
    path('create-visit/', views.create_visit, name="create_visit"),
    path("api/branches/", BranchListView.as_view(), name="branch_list"),
    path("api/rooms/", RoomListView.as_view(), name="room_list"),
    path("api/visits/<int:pk>/", UpdateVisitView.as_view(), name="update_visit_api"),  # ✅ Должно быть здесь!
    path('api/filtered-visits/', FilteredVisitRecords.as_view(), name='filtered_visits'),  # Путь для фильтрации визитов
    path('api/get_filtered_visits/', views.get_filtered_visits, name='get_filtered_visits'),
    path('api/visit/', views.VisitRecordViewSet.as_view({'get': 'list'}), name='visit_record_list'),
    path('api/visit/create/', views.create_visit, name='create_visit'),
    path('api/visit/<int:visit_id>/update/', views.update_visit, name='update_visit'),
    path('api/visit/<int:visit_id>/delete/', views.DeleteVisitRecordView.as_view(), name='delete_visit'),
    path('api/specializations/', SpecializationListView.as_view(), name='specializations'),
    
    

    
]
