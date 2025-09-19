from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False

class IsPatientOwner(permissions.BasePermission):
    """
    Permission to check if user owns the patient
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsAppointmentOwner(permissions.BasePermission):
    """
    Permission to check if user owns the appointment
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsDoctorOrAdmin(permissions.BasePermission):
    """
    Permission for doctor-specific actions
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return False
            
        return (profile.role in ['DOCTOR', 'ADMIN'] or 
                request.user.is_staff or 
                request.user.is_superuser)
