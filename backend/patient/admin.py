from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'relation', 'gender', 'age', 'created_at')
    list_filter = ('gender', 'relation', 'created_at')
    search_fields = ('first_name', 'last_name', 'user__email')
    ordering = ('-created_at',)

# appointment/admin.py
from django.contrib import admin
from appointment.models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'patient', 'doctor', 'availability', 
        'status', 'appointment_fee', 'created_at'
    )
    list_filter = ('status', 'created_at', 'doctor__specialization')
    search_fields = (
        'patient__first_name', 'patient__last_name',
        'doctor__first_name', 'doctor__last_name'
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')