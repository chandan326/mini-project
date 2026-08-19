import uuid
from django.db import models
from django.conf import settings
from crops.models import Crop
from diseases.models import Disease

class Diagnosis(models.Model):
    STATUS_CHOICES = [
        ('QUEUED', 'Queued'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    RETENTION_CHOICES = [
        ('TEMPORARY', 'Temporary Storage'),
        ('PROCESSED', 'Processed & Retained for Model Training'),
        ('STORED_WITH_USER_PERMISSION', 'Stored with User Permission'),
        ('DELETED', 'Deleted per Privacy Policy'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='diagnoses')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='diagnoses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PROCESSING')
    predicted_disease = models.ForeignKey(Disease, on_delete=models.SET_NULL, null=True, blank=True, related_name='diagnoses')
    confidence_score = models.FloatField(default=0.0)
    is_low_confidence = models.BooleanField(default=False)
    is_inconsistent = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)
    image_retention_status = models.CharField(max_length=40, choices=RETENTION_CHOICES, default='PROCESSED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Diagnoses'

    def __str__(self):
        disease_name = self.predicted_disease.name if self.predicted_disease else "Unknown / Low Confidence"
        return f"Diagnosis {str(self.id)[:8]} - {self.crop.name} ({disease_name})"

    @property
    def confidence_pct(self):
        return int(self.confidence_score * 100)

class DiagnosisImage(models.Model):
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.CASCADE, related_name='images')
    slot_number = models.PositiveSmallIntegerField(default=1, help_text="Slot index 1 to 5")
    image = models.ImageField(upload_to='diagnosis_uploads/%Y/%m/%d/')
    is_valid = models.BooleanField(default=True)
    quality_warning = models.CharField(max_length=255, blank=True, null=True)
    prediction_prob = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['slot_number']

    def __str__(self):
        return f"Slot {self.slot_number} Image for Diagnosis {str(self.diagnosis.id)[:8]}"

class DiagnosisAnswer(models.Model):
    diagnosis = models.OneToOneField(Diagnosis, on_delete=models.CASCADE, related_name='answers')
    first_noticed = models.CharField(max_length=50, default='Today', help_text="e.g. Today, 2-3 days ago, About a week ago, >1 week ago")
    affected_parts = models.JSONField(default=list, help_text="e.g. ['Leaves', 'Stem']")
    visible_symptoms = models.JSONField(default=list, help_text="e.g. ['Yellowing', 'Brown spots']")
    is_spreading = models.CharField(max_length=20, default='Not sure')
    weather_condition = models.CharField(max_length=50, default='Humid')
    treatment_applied = models.CharField(max_length=20, default='No')
    treatment_details = models.TextField(blank=True)

    def __str__(self):
        return f"Questionnaire Answers for Diagnosis {str(self.diagnosis.id)[:8]}"

class Feedback(models.Model):
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.CASCADE, related_name='feedbacks')
    is_helpful = models.BooleanField(default=True)
    reason = models.CharField(max_length=100, blank=True, null=True)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        val = "Helpful" if self.is_helpful else "Unhelpful"
        return f"Feedback ({val}) for {str(self.diagnosis.id)[:8]}"
