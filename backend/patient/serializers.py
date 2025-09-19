from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Patient
        fields = [
            'id', 'title', 'first_name', 'last_name', 'full_name',
            'relation', 'gender', 'age', 'medical_history',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_age(self, value):
        if value <= 0 or value > 150:
            raise serializers.ValidationError("Age must be between 1 and 150")
        return value

    def validate(self, data):
        user = self.context['request'].user
        
        # Check if trying to add more than 4 patients
        if not self.instance:  # Creating new patient
            if user.patients.count() >= 4:
                raise serializers.ValidationError(
                    "You can only add up to 4 patients."
                )
        
        # Check for duplicate relation (except when updating same instance)
        relation = data.get('relation')
        if relation:
            existing = user.patients.filter(relation=relation)
            if self.instance:
                existing = existing.exclude(id=self.instance.id)
            
            if existing.exists():
                raise serializers.ValidationError(
                    f"You already have a patient with relation '{relation}'"
                )
        
        return data