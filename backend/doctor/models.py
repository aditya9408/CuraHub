from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date, time

class Doctor(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    SPECIALIZATIONS = [
        ('cardiology', 'Cardiology'),
        ('dermatology', 'Dermatology'),
        ('endocrinology', 'Endocrinology'),
        ('gastroenterology', 'Gastroenterology'),
        ('general_medicine', 'General Medicine'),
        ('neurology', 'Neurology'),
        ('oncology', 'Oncology'),
        ('orthopedics', 'Orthopedics'),
        ('pediatrics', 'Pediatrics'),
        ('psychiatry', 'Psychiatry'),
        ('radiology', 'Radiology'),
        ('surgery', 'Surgery'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(
        validators=[MinValueValidator(25), MaxValueValidator(80)]
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()
    specialization = models.CharField(max_length=50, choices=SPECIALIZATIONS)
    license_no = models.CharField(max_length=100, unique=True)
    experience = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(60)]
    )
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to="doctors/photos/", blank=True, null=True)
    consultation_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=500.00
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} - {self.get_specialization_display()}"

    @property
    def full_name(self):
        return f"Dr. {self.first_name} {self.last_name}"

class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(
        Doctor, 
        on_delete=models.CASCADE, 
        related_name="availabilities"
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')
        ordering = ['date', 'start_time']

    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.date < date.today():
            raise ValidationError({'date': 'Cannot set availability for past dates'})
        
        if self.start_time >= self.end_time:
            raise ValidationError({'end_time': 'End time must be after start time'})
        
        # Check for overlapping slots
        overlapping = DoctorAvailability.objects.filter(
            doctor=self.doctor,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )
        
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)
            
        if overlapping.exists():
            raise ValidationError('This time slot overlaps with existing availability')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.doctor.full_name} - {self.date} ({self.start_time}-{self.end_time})"
