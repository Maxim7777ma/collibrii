from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from django.core.exceptions import ValidationError
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
from .models import Nurse, ServicePriceList, VisitRecord, Doctor, Pacient,ClinicRoom,Specialization
from .serializers import NurseSerializer, ServiceSerializer, VisitSerializer, DoctorSerializer, PatientSerializer,SpecializationSerializer



from rest_framework.generics import UpdateAPIView
from .serializers import ClinicBranchSerializer, ClinicRoomSerializer
from .models import ClinicBranch, ClinicRoom
from rest_framework.decorators import api_view
from django.shortcuts import render, redirect
from .models import Pacient, Doctor, Nurse, ServicePriceList, VisitRecord
from django.contrib import messages


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json

from .models import VisitRecord
from .serializers import VisitSerializer
from rest_framework.generics import RetrieveUpdateAPIView
from django.db.models import Q


def get_filtered_visits(request):
    filters = request.data  # Получаем фильтры с фронта

    visits = VisitRecord.objects.all()

    # Применяем фильтры
    if filters.get('branch'):
        visits = visits.filter(clinic_branch_id=filters['branch'])
    if filters.get('room'):
        visits = visits.filter(clinic_room_id=filters['room'])
    if filters.get('doctor'):
        visits = visits.filter(doctor_id=filters['doctor'])
    if filters.get('patient'):
        visits = visits.filter(patient_id=filters['patient'])
    
    # Отправляем отфильтрованные визиты
    return JsonResponse(list(visits.values()), safe=False)


class FilteredVisitRecords(APIView):
    def post(self, request):
        try:
            filters = request.data
            queryset = VisitRecord.objects.all()

            # Фильтрация по филиалу
            if 'clinic_branch' in filters:
                queryset = queryset.filter(clinic_branch_id=filters['clinic_branch'])

            # Фильтрация по кабинету
            if 'clinic_room' in filters:
                queryset = queryset.filter(clinic_room_id=filters['clinic_room'])

            # Фильтрация по специализации врача
            if 'specialization' in filters:
                queryset = queryset.filter(doctor__specializations__id=filters['specialization'])

            # Фильтрация по врачу
            if 'doctor' in filters:
                queryset = queryset.filter(doctor_id=filters['doctor'])

            # Фильтрация по пациенту
            if 'patient' in filters:
                queryset = queryset.filter(patient_id=filters['patient'])

            # Сериализация данных
            serializer = VisitRecordSerializer(queryset, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class SpecializationListView(APIView):
    def get(self, request):
        specializations = Specialization.objects.all()
        serializer = SpecializationSerializer(specializations, many=True)
        return Response(serializer.data)

class VisitViewSet(viewsets.ModelViewSet):
    queryset = VisitRecord.objects.all()
    serializer_class = VisitRecordSerializer  # ✅ Используем кастомный сериализатор


class UpdateVisitView(RetrieveUpdateAPIView):
    """✅ API для обновления времени начала, окончания и длительности визита"""
    queryset = VisitRecord.objects.all()
    serializer_class = VisitSerializer

    def patch(self, request, *args, **kwargs):
        visit = get_object_or_404(VisitRecord, pk=kwargs["pk"])  # ✅ Теперь 404 если нет записи
        data = request.data

        visit.patient_id = data.get("patient") or visit.patient_id
        visit.doctor_id = data.get("doctor") or visit.doctor_id
        visit.visit_date = data.get("visit_date") or visit.visit_date
        visit.visit_time = data.get("visit_time") or visit.visit_time
        visit.visit_end_time = data.get("visit_end_time") or visit.visit_end_time
        visit.duration_minutes = data.get("duration_minutes") or visit.duration_minutes
        visit.description = data.get("description") or visit.description
        visit.payment_status = data.get("payment_status") or visit.payment_status
        visit.discount_percent = data.get("discount_percent", visit.discount_percent)

        # Обновляем список услуг со скидкой
        discounted = data.get("discounted_services")
        if discounted is not None:
            visit.discounted_services.set(discounted)

        # ✅ Фикс обновления филиала и кабинета
        if "clinic_branch" in data:
            visit.clinic_branch = ClinicBranch.objects.get(pk=data["clinic_branch"])
        if "clinic_room" in data:
            visit.clinic_room = ClinicRoom.objects.get(pk=data["clinic_room"])

        visit.save()
        print("✅ Данные после сохранения:", visit.clinic_branch_id, visit.clinic_room_id)  # 👉 Посмотри, что реально сохраняется
        return Response({"message": "✅ Запись обновлена!"}, status=status.HTTP_200_OK)


def update_visit(request, visit_id):
    """✅ Исправленный API для обновления визита"""
    if request.method != "PATCH":
        return JsonResponse({"error": "Метод не поддерживается"}, status=405)

    try:
        visit = VisitRecord.objects.get(id=visit_id)
        data = json.loads(request.body)

        visit.patient_id = data.get("patient", visit.patient_id)
        visit.doctor_id = data.get("doctor", visit.doctor_id)
        visit.visit_date = data.get("visit_date", visit.visit_date)
        visit.visit_time = data.get("visit_time", visit.visit_time)
        visit.visit_end_time = data.get("visit_end_time", visit.visit_end_time)
        visit.description = data.get("description", visit.description)
        visit.payment_status = data.get("payment_status", visit.payment_status)

        # 🔥 Обновляем Many-to-Many поле "услуги"
        services = data.get("services_ids") or data.get("services")
        if services is not None:
            visit.services.set(services)

        visit.save()
        return JsonResponse({"message": "✅ Визит обновлен"}, status=200)

    except VisitRecord.DoesNotExist:
        return JsonResponse({"error": "❌ Визит не найден"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


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

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return VisitRecordSerializer
        return VisitSerializer

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

    def get_serializer_class(self):
        if self.request.method == "POST":
            return VisitRecordSerializer  # для создания
        return VisitSerializer  # для отображения
    
    def perform_create(self, serializer):
        serializer.save()  # логика уже внутри сериализатора

class NurseListView(generics.ListAPIView):
    queryset = Nurse.objects.all()
    serializer_class = NurseSerializer

class ServiceListView(generics.ListAPIView):
    queryset = ServicePriceList.objects.all().order_by("subgroup_number", "service_code")
    serializer_class = ServiceSerializer

class DoctorListView(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

class PatientListView(generics.ListAPIView):
    queryset = Pacient.objects.all()
    serializer_class = PatientSerializer

class ClinicRoomViewSet(viewsets.ModelViewSet):
    queryset = ClinicRoom.objects.all()
    serializer_class = ClinicRoomSerializer

    def get_queryset(self):
        branch_id = self.request.query_params.get("branch")

        if not branch_id or not branch_id.isdigit():
            raise ValidationError("❌ Некорректный branch_id: ожидается число!")

        return ClinicRoom.objects.filter(branch_id=branch_id)

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
        if branch_id and branch_id.isdigit():  # ✅ Проверка, что это число
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
    services = list(ServicePriceList.objects.values("id", "subgroup_number", "subgroup_name", "service_code", "service_name", "service_price"))
    return JsonResponse(services, safe=False)





def index(request):
    patients = Pacient.objects.all()
    doctors = Doctor.objects.all()
    nurses = Nurse.objects.all()
    services = ServicePriceList.objects.all().order_by("subgroup_number", "service_code")  # 🔹 Сортировка по подгруппам

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

