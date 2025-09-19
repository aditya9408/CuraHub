from rest_framework import serializers
from .models import Appointment
from patient.models import Patient
from doctor.models import DoctorAvailability

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    doctor_specialization = serializers.CharField(
        source='doctor.get_specialization_display', 
        read_only=True
    )
    date = serializers.DateField(source='availability.date', read_only=True)
    start_time = serializers.TimeField(source='availability.start_time', read_only=True)
    end_time = serializers.TimeField(source='availability.end_time', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 
            'doctor_name', 'doctor_specialization',
            'availability', 'date', 'start_time', 'end_time',
            'symptoms', 'additional_notes', 'status', 
            'appointment_fee', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'doctor', 'appointment_fee', 'created_at', 'updated_at'
        ]

    def validate_patient(self, value):
        """Ensure patient belongs to the requesting user"""
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError(
                "You can only book appointments for your own patients"
            )
        return value

    def validate_availability(self, value):
        """Ensure availability slot is available and valid"""
        if not value.is_available:
            raise serializers.ValidationError("This time slot is not available")
        
        if hasattr(value, 'appointment'):
            raise serializers.ValidationError("This slot is already booked")
            
        # Check if it's not in the past
        from datetime import date, datetime, time
        now = datetime.now()
        appointment_datetime = datetime.combine(value.date, value.start_time)
        
        if appointment_datetime <= now:
            raise serializers.ValidationError(
                "Cannot book appointments for past time slots"
            )
            
        return value

    def validate_symptoms(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Please provide more detailed symptoms (at least 10 characters)"
            )
        return value.strip()

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        validated_data['doctor'] = validated_data['availability'].doctor
        return super().create(validated_data)

class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """Separate serializer for updates - limited fields"""
    
    class Meta:
        model = Appointment
        fields = ['symptoms', 'additional_notes', 'status']

    def validate_status(self, value):
        """Only allow certain status transitions"""
        if self.instance:
            current_status = self.instance.status
            
            # Define allowed transitions
            allowed_transitions = {
                'PENDING': ['CONFIRMED', 'CANCELLED'],
                'CONFIRMED': ['COMPLETED', 'CANCELLED', 'NO_SHOW'],
                'CANCELLED': [],  # Cannot change from cancelled
                'COMPLETED': [],  # Cannot change from completed
                'NO_SHOW': [],    # Cannot change from no-show
            }
            
            if value not in allowed_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot change status from {current_status} to {value}"
                )
        
        return value
