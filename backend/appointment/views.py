from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentUpdateSerializer

class AppointmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'doctor', 'patient']
    search_fields = ['symptoms', 'doctor__first_name', 'doctor__last_name']
    ordering_fields = ['created_at', 'availability__date']
    ordering = ['-created_at']

    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user).select_related(
            'patient', 'doctor', 'availability'
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            appointment = serializer.save()
            return Response({
                'message': 'Appointment booked successfully',
                'appointment': AppointmentSerializer(
                    appointment, 
                    context={'request': request}
                ).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user).select_related(
            'patient', 'doctor', 'availability'
        )
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AppointmentUpdateSerializer
        return AppointmentSerializer

    def destroy(self, request, *args, **kwargs):
        appointment = self.get_object()
        
        # Only allow cancellation if appointment is pending or confirmed
        if appointment.status not in ['PENDING', 'CONFIRMED']:
            return Response({
                'error': 'Cannot cancel appointment with current status'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update status instead of deleting
        appointment.status = 'CANCELLED'
        appointment.save()
        
        return Response({
            'message': 'Appointment cancelled successfully'
        }, status=status.HTTP_200_OK)