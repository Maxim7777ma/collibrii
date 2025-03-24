from rest_framework import serializers
from .models import Nurse, ServicePriceList, VisitRecord, Doctor, Pacient,ClinicRoom,ClinicBranch
from rest_framework.generics import RetrieveUpdateAPIView

class VisitRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.fool_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.fool_name', read_only=True)
    nurse_name = serializers.CharField(source='nurse.fool_name', read_only=True)


    class Meta:
        model = VisitRecord
        fields = '__all__'  # Теперь используем все поля
    


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

    class Meta:
        model = VisitRecord
        fields = '__all__'




class UpdateVisitView(RetrieveUpdateAPIView):  # ✅ Теперь поддерживает и GET, и PATCH
    """API для получения и обновления визита"""
    queryset = VisitRecord.objects.all()
    serializer_class = VisitSerializer   