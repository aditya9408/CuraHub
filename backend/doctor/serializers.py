from rest_framework import serializers
from .models import Doctor, DoctorAvailability
from datetime import date

class DoctorSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    specialization_display = serializers.CharField(
        source='get_specialization_display', 
        read_only=True
    )
    
    class Meta:
        model = Doctor
        fields = [
            "id", "first_name", "last_name", "full_name",
            "specialization", "specialization_display", 
            "license_no", "experience", "consultation_fee",
            "photo", "is_active"
        ]

class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    doctor_specialization = serializers.CharField(
        source='doctor.get_specialization_display', 
        read_only=True
    )

    class Meta:
        model = DoctorAvailability
        fields = [
            "id", "doctor", "doctor_name", "doctor_specialization", 
            "date", "start_time", "end_time", "is_available"
        ]
        
    def validate_date(self, value):
        if value < date.today():
            raise serializers.ValidationError(
                "Cannot set availability for past dates"
            )
        return value

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError(
                {"end_time": "End time must be after start time"}
            )
        return data