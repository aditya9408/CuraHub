from django.urls import path
from .views import (
    DoctorListView, DoctorDetailView,
    DoctorAvailabilityListView, DoctorAvailabilityCreateView
)

urlpatterns = [
    path('', DoctorListView.as_view(), name='doctor-list'),
    path('<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),
    path('availability/', DoctorAvailabilityListView.as_view(), name='doctor-availability-list'),
    path('availability/create/', DoctorAvailabilityCreateView.as_view(), name='doctor-availability-create'),
]