from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),  # Fixed: Add api/ prefix
    path('api/patients/', include('patient.urls')),  # Fixed: plural and api prefix
    path('api/doctors/', include('doctor.urls')),  # Fixed: plural and api prefix
    path('api/appointments/', include('appointment.urls')),  # Fixed: plural and api prefix
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)