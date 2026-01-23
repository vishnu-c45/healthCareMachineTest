from rest_framework import serializers
from datetime import date


class PatientSerializer(serializers.Serializer):
    resourceType = serializers.CharField()
    id = serializers.CharField()
    birthDate = serializers.DateField()
    gender = serializers.CharField()
    name = serializers.ListField()
    identifier = serializers.ListField(required=False)
    telecom = serializers.ListField(required=False)

    def validate_birthDate(self, value):
        age = date.today().year - value.year
        if age < 18:
            raise serializers.ValidationError("Patient must be 18 or older.")
        return value
