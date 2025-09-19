from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import date, timedelta
from .models import DoctorAvailability, Doctor
from .serializers import DoctorAvailabilitySerializer, DoctorSerializer

class DoctorListView(generics.ListAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization', 'is_active']
    search_fields = ['first_name', 'last_name', 'specialization']
    ordering_fields = ['experience', 'consultation_fee', 'first_name']
    ordering = ['first_name']
    
    def get_queryset(self):
        return Doctor.objects.filter(is_active=True)

class DoctorDetailView(generics.RetrieveAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Doctor.objects.filter(is_active=True)

class DoctorAvailabilityListView(generics.ListAPIView):
    serializer_class = DoctorAvailabilitySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['doctor', 'date', 'is_available']
    ordering = ['date', 'start_time']

    def get_queryset(self):
        queryset = DoctorAvailability.objects.filter(
            date__gte=date.today(),
            is_available=True
        )
        
        doctor_id = self.request.query_params.get('doctor')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
            
        # Get next 30 days by default
        end_date = date.today() + timedelta(days=30)
        queryset = queryset.filter(date__lte=end_date)
        
        return queryset

class DoctorAvailabilityCreateView(generics.CreateAPIView):
    serializer_class = DoctorAvailabilitySerializer
    permission_classes = [permissions.IsAdminUser]  # Only admin can create slots
