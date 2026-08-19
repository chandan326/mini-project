from django.contrib import admin
from .models import Disease, Symptom, DiseaseSymptom

class DiseaseSymptomInline(admin.TabularInline):
    model = DiseaseSymptom
    extra = 1

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_hi', 'crop', 'severity', 'active', 'created_at')
    list_filter = ('crop', 'severity', 'active')
    search_fields = ('name', 'name_hi', 'scientific_name', 'description')
    inlines = [DiseaseSymptomInline]

@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_hi', 'code', 'icon')
    search_fields = ('name', 'name_hi', 'code')
