from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from patient.models import Patient
from doctor.models import Doctor, DoctorAvailability

class Appointment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("COMPLETED", "Completed"),
        ("NO_SHOW", "No Show"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="appointments"
    )
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE, 
        related_name="appointments"
    )
    doctor = models.ForeignKey(
        Doctor, 
        on_delete=models.CASCADE, 
        related_name="appointments"
    )
    availability = models.OneToOneField(  # Changed to OneToOne
        DoctorAvailability, 
        on_delete=models.CASCADE, 
        related_name="appointment"
    )
    
    symptoms = models.TextField()
    additional_notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default="PENDING"
    )
    appointment_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        # Ensure patient belongs to the user
        if hasattr(self, 'user') and hasattr(self, 'patient'):
            if self.patient.user != self.user:
                raise ValidationError(
                    {'patient': 'You can only book appointments for your own patients'}
                )
        
        # Ensure availability is not already booked
        if hasattr(self, 'availability'):
            if hasattr(self.availability, 'appointment') and self.availability.appointment != self:
                raise ValidationError(
                    {'availability': 'This time slot is already booked'}
                )

    def save(self, *args, **kwargs):
        # Set appointment fee from doctor's consultation fee
        if not self.appointment_fee and hasattr(self, 'doctor'):
            self.appointment_fee = self.doctor.consultation_fee
            
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Mark availability as unavailable
        if self.availability:
            self.availability.is_available = False
            self.availability.save()

    def delete(self, *args, **kwargs):
        # Mark availability as available again when appointment is deleted
        if self.availability:
            self.availability.is_available = True
            self.availability.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Appointment: {self.patient.full_name} with {self.doctor.full_name} on {self.availability.date}"
