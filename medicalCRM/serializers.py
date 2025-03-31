from rest_framework import serializers
from .models import Nurse, ServicePriceList, VisitRecord, Doctor, Pacient,ClinicRoom,ClinicBranch,Specialization
from rest_framework.generics import RetrieveUpdateAPIView
from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response








class VisitRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.fool_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.fool_name', read_only=True)
    nurse_name = serializers.CharField(source='nurse.fool_name', read_only=True)

    discount_percent = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    services_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    discounted_services_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )


    class Meta:
        model = VisitRecord
        fields = '__all__'  # Теперь используем все поля

    
    def create(self, validated_data):
        services_ids = validated_data.pop("services_ids", [])
        discounted_ids = validated_data.pop("discounted_services_ids", [])

        visit = VisitRecord(**validated_data)
        visit.save()  # теперь у него есть ID

        # 🔹 Устанавливаем услуги
        if services_ids:
            visit.services.set(services_ids)
        if discounted_ids:
            visit.discounted_services.set(discounted_ids)

        # ✅ теперь можно посчитать сумму
        visit.total_price = self.calculate_total_price(visit)
        visit.save()

        return visit

    def update(self, instance, validated_data):
        services_ids = validated_data.pop("services_ids", None)
        discounted_ids = validated_data.pop("discounted_services_ids", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if services_ids is not None:
            instance.services.set(services_ids)
        if discounted_ids is not None:
            instance.discounted_services.set(discounted_ids)

        # ✅ пересчёт после установки услуг
        instance.total_price = self.calculate_total_price(instance)
        instance.save()

        return instance
    

    def calculate_total_price(self, visit):
        total = Decimal("0.00")
        discount_percent = visit.discount_percent or Decimal("0.00")
        discounted_ids = set(visit.discounted_services.values_list("id", flat=True))

        for service in visit.services.all():
            price = service.service_price
            if service.id in discounted_ids:
                price = price * (1 - discount_percent / Decimal("100"))
            total += price

        return round(total, 2)  
    


class NurseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nurse
        fields = ['id', 'fool_name']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePriceList
        fields = ["id", "subgroup_number", "subgroup_name", "service_code", "service_name", "service_price"]
    
    def get_service_info(self, obj):
        return f"[{obj.subgroup_number}] {obj.subgroup_name} → {obj.service_code} - {obj.service_name} ({obj.service_price} грн)"

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'fool_name']

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pacient
        fields = ['id', 'fool_name']


class ClinicBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicBranch
        fields = "__all__"

class ClinicRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicRoom
        fields = "__all__"  

  


class VisitSerializer(serializers.ModelSerializer):
    """Сериализатор для визита с поддержкой отображения названий и передачи ID"""
    
    # ✅ Читаем названия филиала и кабинета
    clinic_branch_name = serializers.CharField(source="clinic_branch.branch_name", read_only=True)
    clinic_room_number = serializers.CharField(source="clinic_room.room_number", read_only=True)

    # ✅ Читаем имена
    patient_name = serializers.CharField(source='patient.fool_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.fool_name', read_only=True)
    nurse_name = serializers.CharField(source='nurse.fool_name', read_only=True)

    # ✅ Читаем услуги как список строк
    
    services = ServiceSerializer(many=True, read_only=True)

    # ✅ Передаём ID при обновлении через `PrimaryKeyRelatedField`
    clinic_branch = serializers.PrimaryKeyRelatedField(
        queryset=ClinicBranch.objects.all(), write_only=True
    )
    clinic_room = serializers.PrimaryKeyRelatedField(
        queryset=ClinicRoom.objects.all(), write_only=True
    )

    services_ids = serializers.PrimaryKeyRelatedField(
        queryset=ServicePriceList.objects.all(), many=True, source="services", write_only=True
    )

    discount_percent = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        default=0.00
    )
    discounted_services_ids = serializers.PrimaryKeyRelatedField(
        queryset=ServicePriceList.objects.all(),
        many=True,
        required=False,
        write_only=True,
        source="discounted_services"
    )

    class Meta:
        model = VisitRecord
        fields = '__all__'




class UpdateVisitView(RetrieveUpdateAPIView):  # ✅ Теперь поддерживает и GET, и PATCH
    """API для получения и обновления визита"""
    queryset = VisitRecord.objects.all()
    serializer_class = VisitSerializer   



class FilteredVisitRecords(APIView):
    def post(self, request):
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
    
class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ['id', 'name']  # Указываем поля, которые хотим сериализовать
