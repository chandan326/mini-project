from rest_framework import serializers
from .models import Diagnosis, DiagnosisImage, DiagnosisAnswer, Feedback
from crops.serializers import CropSerializer
from diseases.serializers import DiseaseSerializer

class DiagnosisImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosisImage
        fields = ['id', 'slot_number', 'image', 'is_valid', 'quality_warning', 'prediction_prob']

class DiagnosisAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosisAnswer
        fields = ['first_noticed', 'affected_parts', 'visible_symptoms', 'is_spreading', 'weather_condition', 'treatment_applied', 'treatment_details']

class DiagnosisSerializer(serializers.ModelSerializer):
    crop = CropSerializer(read_only=True)
    predicted_disease = DiseaseSerializer(read_only=True)
    images = DiagnosisImageSerializer(many=True, read_only=True)
    answers = DiagnosisAnswerSerializer(read_only=True)
    confidence_pct = serializers.ReadOnlyField()

    class Meta:
        model = Diagnosis
        fields = [
            'id', 'crop', 'status', 'predicted_disease', 'confidence_score',
            'confidence_pct', 'is_low_confidence', 'is_inconsistent',
            'explanation', 'image_retention_status', 'created_at', 'images', 'answers'
        ]

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'diagnosis', 'is_helpful', 'reason', 'comments', 'created_at']
