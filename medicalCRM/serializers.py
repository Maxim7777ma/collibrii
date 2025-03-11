from rest_framework import serializers
from .models import Nurse, ServicePriceList, VisitRecord, Doctor, Pacient,ClinicRoom,ClinicBranch

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
        fields = ["id", "service_code", "service_name", "service_price"]

    def get_service_info(self, obj):
        return f"{obj.service_code} - {obj.service_name} ({obj.service_price} грн)"

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'fool_name']

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pacient
        fields = ['id', 'fool_name']


class VisitSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.fool_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.fool_name', read_only=True)
    nurse_name = serializers.CharField(source='nurse.fool_name', read_only=True)

    class Meta:
        model = VisitRecord
        fields = '__all__'  # Используем все поля



class ClinicBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicBranch
        fields = "__all__"

class ClinicRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicRoom
        fields = "__all__"        