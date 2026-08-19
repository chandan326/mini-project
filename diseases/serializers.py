from rest_framework import serializers
from .models import Disease, Symptom, DiseaseSymptom

class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = ['id', 'name', 'name_hi', 'code', 'icon', 'description']

class DiseaseSerializer(serializers.ModelSerializer):
    symptoms = SymptomSerializer(many=True, read_only=True)
    crop_name = serializers.CharField(source='crop.name', read_only=True)
    crop_name_hi = serializers.CharField(source='crop.name_hi', read_only=True)

    class Meta:
        model = Disease
        fields = [
            'id', 'name', 'name_hi', 'scientific_name', 'crop', 'crop_name', 'crop_name_hi',
            'description', 'severity', 'image', 'source_reference', 'symptoms', 'active'
        ]
