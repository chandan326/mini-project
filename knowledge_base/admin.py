from django.contrib import admin
from .models import KnowledgeSource

@admin.register(KnowledgeSource)
class KnowledgeSourceAdmin(admin.ModelAdmin):
    list_display = ('disease', 'title', 'source_reference', 'last_reviewed')
    search_fields = ('disease__name', 'disease__crop__name', 'title', 'causes', 'symptoms_summary')
