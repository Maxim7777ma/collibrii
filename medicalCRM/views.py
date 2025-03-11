from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.generics import ListAPIView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from .models import VisitRecord, Doctor, Pacient
from .serializers import VisitRecordSerializer, DoctorSerializer, PatientSerializer
from django.http import JsonResponse
from .models import Doctor, Pacient, Nurse, ServicePriceList

from rest_framework import generics
from .models import Nurse, ServicePriceList, VisitRecord, Doctor, Pacient,ClinicRoom
from .serializers import NurseSerializer, ServiceSerializer, VisitSerializer, DoctorSerializer, PatientSerializer

from rest_framework.generics import UpdateAPIView
from .serializers import ClinicBranchSerializer, ClinicRoomSerializer
from .models import ClinicBranch, ClinicRoom
from rest_framework.decorators import api_view
from django.shortcuts import render, redirect
from .models import Pacient, Doctor, Nurse, ServicePriceList, VisitRecord
from django.contrib import messages


class UpdateVisitView(UpdateAPIView):
    """✅ API для обновления времени начала, окончания и длительности визита"""
    queryset = VisitRecord.objects.all()
    serializer_class = VisitSerializer

    def patch(self, request, *args, **kwargs):
        visit = get_object_or_404(VisitRecord, pk=kwargs["pk"])  # ✅ Теперь 404 если нет записи
        data = request.data

        visit.visit_date = data.get("visit_date", visit.visit_date)
        visit.visit_time = data.get("visit_time", visit.visit_time)
        visit.visit_end_time = data.get("visit_end_time", visit.visit_end_time)
        visit.duration_minutes = data.get("duration_minutes", visit.duration_minutes)

        visit.save()
        return Response({"message": "✅ Запись обновлена!"}, status=status.HTTP_200_OK)
    
class DeleteVisitRecordView(APIView):
    """❌ Удаление записи о визите"""
    def delete(self, request, record_id):
        visit = get_object_or_404(VisitRecord, pk=record_id)
        visit.delete()
        return Response({"message": f"✅ Запись {record_id} удалена."}, status=status.HTTP_204_NO_CONTENT)

class VisitRecordViewSet(viewsets.ModelViewSet):
    """📅 API для управления записями на прием"""
    queryset = VisitRecord.objects.all()
    serializer_class = VisitRecordSerializer

    def create(self, request, *args, **kwargs):
        """Создание новой записи"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """Обновление записи (перемещение, изменение времени)"""
        visit_record = get_object_or_404(VisitRecord, pk=pk)
        serializer = VisitRecordSerializer(visit_record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Удаление записи"""
        visit_record = get_object_or_404(VisitRecord, pk=pk)
        visit_record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class VisitListCreateView(generics.ListCreateAPIView):
    queryset = VisitRecord.objects.all()
    serializer_class = VisitSerializer

    def perform_create(self, serializer):
        visit = serializer.save()
        # Пересчитываем время окончания приёма
        visit.save()

class NurseListView(generics.ListAPIView):
    queryset = Nurse.objects.all()
    serializer_class = NurseSerializer

class ServiceListView(generics.ListAPIView):
    queryset = ServicePriceList.objects.all()
    serializer_class = ServiceSerializer

class DoctorListView(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

class PatientListView(generics.ListAPIView):
    queryset = Pacient.objects.all()
    serializer_class = PatientSerializer

class ClinicRoomViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        branch_id = self.request.query_params.get('branch', None)
        queryset = ClinicRoom.objects.all()
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        return queryset

class BranchListView(ListAPIView):
    queryset = ClinicBranch.objects.all()
    serializer_class = ClinicBranchSerializer
    permission_classes = [AllowAny]


class RoomListView(ListAPIView):
    queryset = ClinicRoom.objects.all()
    serializer_class = ClinicRoomSerializer
    permission_classes = [AllowAny]  # 👈 Открывает доступ для всех


    def get_queryset(self):
        branch_id = self.request.query_params.get("branch")
        if branch_id:
            return ClinicRoom.objects.filter(branch_id=branch_id)  # Исправленный фильтр
        return ClinicRoom.objects.all()




def get_doctors(request):
    doctors = list(Doctor.objects.values('id', 'full_name'))
    return JsonResponse(doctors, safe=False)

def get_patients(request):
    patients = list(Pacient.objects.values('id', 'full_name'))
    return JsonResponse(patients, safe=False)

def get_nurses(request):
    nurses = list(Nurse.objects.values('id', 'full_name'))
    return JsonResponse(nurses, safe=False)

def get_services(request):
    services = list(ServicePriceList.objects.values('id', 'service_name', 'service_price'))
    return JsonResponse(services, safe=False)





def index(request):
    patients = Pacient.objects.all()
    doctors = Doctor.objects.all()
    nurses = Nurse.objects.all()
    services = ServicePriceList.objects.all()

    return render(request, "medicalCRM/index.html", {
        "patients": patients,
        "doctors": doctors,
        "nurses": nurses,
        "services": services,
    })

def create_visit(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient")
        doctor_id = request.POST.get("doctor")
        nurse_id = request.POST.get("nurse")
        visit_date = request.POST.get("visit_date")
        visit_time = request.POST.get("visit_time")
        service_id = request.POST.get("service")
        payment_status = request.POST.get("payment_status")

        if not patient_id or not doctor_id or not service_id:
            messages.error(request, "Заполните все обязательные поля!")
            return redirect("index")

        patient = Pacient.objects.get(id=patient_id)
        doctor = Doctor.objects.get(id=doctor_id)
        nurse = Nurse.objects.get(id=nurse_id) if nurse_id else None
        service = ServicePriceList.objects.get(id=service_id)

        visit = VisitRecord.objects.create(
            patient=patient,
            doctor=doctor,
            nurse=nurse,
            visit_date=visit_date,
            visit_time=visit_time,
            total_price=service.service_price,
            payment_status=payment_status
        )
        visit.services.add(service)

        messages.success(request, "Запись успешно создана!")
        return redirect("index")

    return redirect("index")

