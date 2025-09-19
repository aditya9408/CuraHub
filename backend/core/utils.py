from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta

def send_appointment_confirmation(appointment):
    """Send appointment confirmation email"""
    subject = f"Appointment Confirmation - {appointment.doctor.full_name}"
    message = f"""
    Dear {appointment.patient.full_name},
    
    Your appointment has been confirmed with {appointment.doctor.full_name}.
    
    Details:
    Date: {appointment.availability.date}
    Time: {appointment.availability.start_time} - {appointment.availability.end_time}
    Doctor: {appointment.doctor.full_name}
    Specialization: {appointment.doctor.get_specialization_display()}
    
    Please arrive 15 minutes before your appointment time.
    
    Best regards,
    Healthcare Management System
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.user.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Failed to send email: {e}")

def get_available_slots(doctor, date_from=None, date_to=None):
    """Get available time slots for a doctor"""
    from doctor.models import DoctorAvailability
    from datetime import date
    
    if not date_from:
        date_from = date.today()
    if not date_to:
        date_to = date_from + timedelta(days=30)
    
    return DoctorAvailability.objects.filter(
        doctor=doctor,
        date__range=[date_from, date_to],
        is_available=True
    ).order_by('date', 'start_time')