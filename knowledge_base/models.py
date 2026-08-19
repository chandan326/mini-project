from django.db import models
from diseases.models import Disease

class KnowledgeSource(models.Model):
    title = models.CharField(max_length=200, help_text="Reference title or article heading")
    disease = models.OneToOneField(Disease, on_delete=models.CASCADE, related_name='knowledge_source')
    symptoms_summary = models.TextField(help_text="Detailed description of visible field symptoms")
    causes = models.TextField(help_text="Pathogen, fungal, bacterial or environmental cause")
    favorable_conditions = models.TextField(help_text="Temperature, humidity or moisture conditions encouraging spread")
    treatment_immediate = models.TextField(help_text="Immediate non-chemical or field care steps")
    treatment_management = models.TextField(help_text="Longer term cultural or approved management practices")
    prevention_methods = models.TextField(help_text="Crop spacing, sanitation, resistant varieties, crop rotation")
    monitoring_guidance = models.TextField(help_text="When and how often to inspect crops, when to seek expert help")
    source_reference = models.CharField(max_length=255, default="Verified ICAR / Agricultural University Guidelines")
    last_reviewed = models.DateField(auto_now=True)

    class Meta:
        verbose_name = "Knowledge Base Entry"
        verbose_name_plural = "Knowledge Base Entries"

    def __str__(self):
        return f"Knowledge Entry: {self.disease.crop.name} - {self.disease.name}"
