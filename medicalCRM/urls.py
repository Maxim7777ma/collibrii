from django.urls import path
from django.shortcuts import render

from .views import (
    VisitListCreateView, NurseListView, ServiceListView, 
    DoctorListView, PatientListView, DeleteVisitRecordView,
    BranchListView, RoomListView,ClinicRoomViewSet,UpdateVisitView
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
    path('api/patients/', PatientListView.as_view(), name='patients'),
    path('calendar/', calendar_view, name='calendar'),  
    path('delete_visit/<int:record_id>/', DeleteVisitRecordView.as_view(), name='delete_visit_record'),
    path('create-visit_start/', views.index, name="index"),
    path('create-visit/', views.create_visit, name="create_visit"),
    path("api/branches/", BranchListView.as_view(), name="branch_list"),
    path("api/rooms/", RoomListView.as_view(), name="room_list"),
    path("api/visits/<int:pk>/", UpdateVisitView.as_view(), name="update_visit_api"),  # ✅ Должно быть здесь!
    
    

    
]
