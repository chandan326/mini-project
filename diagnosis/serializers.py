from rest_framework import serializers
from .models import Diagnosis, DiagnosisImage, DiagnosisAnswer, Feedback
from crops.serializers import CropSerializer
from diseases.serializers import DiseaseSerializer
from crops.models import Crop


class DiagnosisInputSerializer(serializers.Serializer):
    crop_id = serializers.PrimaryKeyRelatedField(queryset=Crop.objects.filter(is_active=True))
    first_noticed = serializers.ChoiceField(choices=['Today', '2-3 days ago', 'About a week ago', 'More than a week ago'], default='Today')
    affected_parts = serializers.ListField(child=serializers.ChoiceField(choices=['Leaves', 'Stem', 'Fruit', 'Roots']), max_length=4, default=list)
    visible_symptoms = serializers.ListField(child=serializers.CharField(max_length=80), max_length=15, default=list)
    is_spreading = serializers.ChoiceField(choices=['Yes', 'No', 'Not sure'], default='Not sure')
    weather_condition = serializers.ChoiceField(choices=['Humid', 'Rainy', 'Dry', 'Very hot', 'Cold'], default='Humid')
    treatment_applied = serializers.ChoiceField(choices=['Yes', 'No'], default='No')
    treatment_details = serializers.CharField(max_length=1000, allow_blank=True, default='')


class FeedbackInputSerializer(serializers.Serializer):
    is_helpful = serializers.BooleanField(required=True)
    reason = serializers.CharField(max_length=100, allow_blank=True, default='')
    comments = serializers.CharField(max_length=2000, allow_blank=True, default='')

    def validate(self, attrs):
        # HTML BooleanField normally treats an absent checkbox as False. These
        # are submit buttons, so an explicit choice must be present.
        if 'is_helpful' not in self.initial_data:
            raise serializers.ValidationError({'is_helpful': 'Choose whether the report was helpful.'})
        return attrs

class DiagnosisImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        from django.urls import reverse
        url = reverse('diagnosis_image', args=[obj.diagnosis_id, obj.pk])
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url

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
    analysis_method = serializers.ReadOnlyField()
    result_url = serializers.SerializerMethodField()

    def get_result_url(self, obj):
        from django.urls import reverse
        return reverse('diagnosis_result', args=[obj.pk])

    class Meta:
        model = Diagnosis
        fields = [
            'id', 'crop', 'status', 'predicted_disease', 'confidence_score',
            'confidence_pct', 'is_low_confidence', 'is_inconsistent',
            'explanation', 'image_retention_status', 'created_at', 'images', 'answers',
            'analysis_method', 'ai_assessment', 'assessed_condition', 'result_url'
        ]

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'diagnosis', 'is_helpful', 'reason', 'comments', 'created_at']
