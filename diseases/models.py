from django.db import models
from crops.models import Crop

class Symptom(models.Model):
    name = models.CharField(max_length=100)
    name_hi = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=50, unique=True, help_text="Unique key identifier e.g. brown_spots")
    icon = models.CharField(max_length=50, default='fa-leaf')
    description = models.TextField(blank=True)

    @property
    def display_name(self):
        from django.utils.translation import get_language
        lang = get_language()
        if lang and lang.startswith('hi') and self.name_hi:
            return self.name_hi
        return self.name

    def __str__(self):
        if self.name_hi:
            return f"{self.name} ({self.name_hi})"
        return self.name

class Disease(models.Model):
    SEVERITY_CHOICES = [
        ('LOW', 'Low Risk / Mild'),
        ('MEDIUM', 'Moderate Risk'),
        ('HIGH', 'High Severity / Critical'),
    ]

    name = models.CharField(max_length=150)
    name_hi = models.CharField(max_length=150, blank=True, null=True)
    scientific_name = models.CharField(max_length=150, blank=True, null=True)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='diseases')
    description = models.TextField()
    symptoms = models.ManyToManyField(Symptom, through='DiseaseSymptom', related_name='diseases')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MEDIUM')
    image = models.ImageField(upload_to='diseases/', blank=True, null=True)
    source_reference = models.CharField(max_length=255, default='Verified Agricultural Knowledge Base')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['crop', 'name']
        unique_together = ('name', 'crop')

    @property
    def display_name(self):
        from django.utils.translation import get_language
        lang = get_language()
        if lang and lang.startswith('hi') and self.name_hi:
            return self.name_hi
        return self.name

    def __str__(self):
        return f"{self.crop.name} - {self.name}"

class DiseaseSymptom(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=True, help_text="True if this is a primary diagnostic symptom")

    class Meta:
        unique_together = ('disease', 'symptom')
