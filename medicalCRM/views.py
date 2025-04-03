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

from datetime import timedelta,datetime

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
import logging


@api_view(['POST'])
def get_filtered_visits(request):
    filters = request.data  # Получаем фильтры с фронта
    print(f"🚀 Полученные фильтры: {filters}")
    print("🔥 Вызвана вьюха: get_filtered_visits", flush=True)

    # Начинаем с пустого Q-объекта (для объединения через AND)
    q_filter = Q()

    # Применяем фильтры через AND
    if 'clinic_branch' in filters and filters['clinic_branch']:
        print(f"📌 Фильтруем по филиалу: {filters['clinic_branch']}")
        q_filter &= Q(clinic_branch_id=filters['clinic_branch'])

    if 'clinic_room' in filters and filters['clinic_room']:
        print(f"📌 Фильтруем по кабинету: {filters['clinic_room']}")
        q_filter &= Q(clinic_room_id=filters['clinic_room'])

    if 'doctor' in filters and filters['doctor']:
        print(f"📌 Фильтруем по врачу: {filters['doctor']}")
        q_filter &= Q(doctor_id=filters['doctor'])

    if 'patient' in filters and filters['patient']:
        print(f"📌 Фильтруем по пациенту: {filters['patient']}")
        q_filter &= Q(patient_id=filters['patient'])

    # Фильтрация по дате начала
    if 'start_date' in filters and filters['start_date']:
        print(f"📌 Фильтруем по дате начала: {filters['start_date']}")
        q_filter &= Q(visit_date__gte=filters['start_date'])

    # Фильтрация по дате окончания
    if 'end_date' in filters and filters['end_date']:
        print(f"📌 Фильтруем по дате окончания: {filters['end_date']}")
        q_filter &= Q(visit_date__lte=filters['end_date'])

    # Применяем все фильтры сразу через объединенный Q-объект
    visits = VisitRecord.objects.filter(q_filter)

    print(f"📥 Найдено визитов: {visits.count()} шт.")
    visits_data = visits.values('id', 'patient__fool_name', 'doctor__fool_name', 'visit_date', 'visit_time', 'total_price')
    print(f"📤 Отправляем на фронт: {list(visits_data)}")
    return JsonResponse(list(visits_data), safe=False)


def get_filtered_visits(request):
    filters = request.data
    queryset = VisitRecord.objects.all()

    # Применение фильтров с помощью Q
    q_filter = Q()
    
    if filters.get('branch'):
        q_filter &= Q(clinic_branch_id=filters['branch'])
    
    if filters.get('room'):
        q_filter &= Q(clinic_room_id=filters['room'])
    
    if filters.get('doctor'):
        q_filter &= Q(doctor_id=filters['doctor'])
    
    if filters.get('patient'):
        q_filter &= Q(patient_id=filters['patient'])

    visits = queryset.filter(q_filter)
    
    # Возвращаем отфильтрованные записи
    return JsonResponse(list(visits.values()), safe=False)



class FilteredVisitRecords(APIView):
    def post(self, request):
        filters = request.data
        print("🔥 Вызвана вьюха: FilteredVisitRecords", flush=True)
        print(f"🚀 Полученные фильтры: {filters}", flush=True)

        # Инициализируем пустой Q-объект для фильтрации
        q_filter = Q()

        # Функция для обработки фильтров
        def safe_int(value):
            try:
                return int(value)
            except (ValueError, TypeError):
                print(f"⚠️ Некорректное значение ID: {value}", flush=True)
                return None

        # Фильтрация по филиалу
        clinic_branch = safe_int(filters.get('clinic_branch'))
        if clinic_branch:
            q_filter &= Q(clinic_branch_id=clinic_branch)
            print(f"📌 Фильтруем по филиалу: {clinic_branch}", flush=True)

        # Фильтрация по кабинету
        clinic_room = safe_int(filters.get('clinic_room'))
        if clinic_room:
            q_filter &= Q(clinic_room_id=clinic_room)
            print(f"📌 Фильтруем по кабинету: {clinic_room}", flush=True)

        # Фильтрация по специализации врача
        specialization = safe_int(filters.get('specialization'))
        if specialization:
            q_filter &= Q(doctor__specializations__id=specialization)
            print(f"📌 Фильтруем по специализации: {specialization}", flush=True)

        # Фильтрация по врачу
        doctor = safe_int(filters.get('doctor'))
        if doctor:
            q_filter &= Q(doctor_id=doctor)
            print(f"📌 Фильтруем по врачу: {doctor}", flush=True)

        # Фильтрация по пациенту
        patient = safe_int(filters.get('patient'))
        if patient:
            q_filter &= Q(patient_id=patient)
            print(f"📌 Фильтруем по пациенту: {patient}", flush=True)

        # Фильтрация по дате начала
        start_date = filters.get('start_date')
        if start_date:
            try:
                q_filter &= Q(visit_date__gte=start_date)
                print(f"📌 Фильтруем по дате начала: {start_date}", flush=True)
            except Exception as e:
                print(f"⚠️ Ошибка в дате начала: {e}", flush=True)

        # Фильтрация по дате окончания
        end_date = filters.get('end_date')
        if end_date:
            try:
                q_filter &= Q(visit_date__lte=end_date)
                print(f"📌 Фильтруем по дате окончания: {end_date}", flush=True)
            except Exception as e:
                print(f"⚠️ Ошибка в дате окончания: {e}", flush=True)

        # Логируем итоговый Q-объект перед фильтрацией
        print(f"🧩 Сформированный Q-объект: {q_filter}", flush=True)

        # Применяем объединенный фильтр к запросу
        queryset = VisitRecord.objects.filter(q_filter)

        # Количество найденных визитов после фильтрации
        print(f"📥 Найдено визитов: {queryset.count()}", flush=True)

        # Сериализация данных
        serializer = VisitRecordSerializer(queryset, many=True)
        print(f"📤 Отправляем на фронт: {serializer.data}", flush=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        
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
        visit.visit_end_date = data.get("visit_end_date") or visit.visit_end_date
        visit.duration_minutes = data.get("duration_minutes") or visit.duration_minutes
        visit.description = data.get("description") or visit.description
        visit.payment_status = data.get("payment_status") or visit.payment_status
        visit.discount_percent = data.get("discount_percent", visit.discount_percent)

        if visit.visit_end_time == "00:00:00" and visit.visit_end_date == visit.visit_date:
            if isinstance(visit.visit_end_date, str):
                visit.visit_end_date = datetime.strptime(visit.visit_end_date, "%Y-%m-%d").date()
            visit.visit_end_date += timedelta(days=1)

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
        visit.visit_end_date = data.get("visit_end_date") or visit.visit_end_date
        visit.visit_end_time = data.get("visit_end_time", visit.visit_end_time)
        visit.description = data.get("description", visit.description)
        visit.payment_status = data.get("payment_status", visit.payment_status)

        # 🔥 Обновляем Many-to-Many поле "услуги"
        services = data.get("services_ids") or data.get("services")
        if services is not None:
            visit.services.set(services)

        
        if visit.visit_end_time == "00:00:00" and visit.visit_end_date == visit.visit_date:
            if isinstance(visit.visit_end_date, str):
                visit.visit_end_date = datetime.strptime(visit.visit_end_date, "%Y-%m-%d").date()
            visit.visit_end_date += timedelta(days=1)    

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
    print("🔥 Вызвана вьюха: VisitRecordViewSet", flush=True)
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
    
class DoctorsBySpecializationAPIView(APIView):
    def get(self, request, specialization_id):
        try:
            doctors = Doctor.objects.filter(specializations__id=specialization_id)
            serializer = DoctorSerializer(doctors, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def doctors_by_specialization(request, specialization_id):
    try:
        doctors = Doctor.objects.filter(specializations__id=specialization_id)
        doctor_data = [{"id": doctor.id, "fool_name": doctor.fool_name} for doctor in doctors]
        return Response(doctor_data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    
    

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

