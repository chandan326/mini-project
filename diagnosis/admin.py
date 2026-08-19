from django.contrib import admin
from .models import Diagnosis, DiagnosisImage, DiagnosisAnswer, Feedback

class DiagnosisImageInline(admin.TabularInline):
    model = DiagnosisImage
    extra = 0
    readonly_fields = ('slot_number', 'image', 'is_valid', 'quality_warning', 'prediction_prob')

class DiagnosisAnswerInline(admin.StackedInline):
    model = DiagnosisAnswer
    extra = 0

@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ('id', 'crop', 'predicted_disease', 'confidence_score_display', 'is_low_confidence', 'is_inconsistent', 'image_retention_status', 'created_at')
    list_filter = ('crop', 'status', 'is_low_confidence', 'is_inconsistent', 'image_retention_status', 'created_at')
    search_fields = ('id', 'crop__name', 'predicted_disease__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [DiagnosisImageInline, DiagnosisAnswerInline]

    def confidence_score_display(self, obj):
        return f"{obj.confidence_pct}%"
    confidence_score_display.short_description = 'Confidence'

    actions = ['set_retention_deleted', 'set_retention_stored_with_permission']

    @admin.action(description="Mark selected diagnoses images as DELETED (Privacy Policy)")
    def set_retention_deleted(self, request, queryset):
        queryset.update(image_retention_status='DELETED')

    @admin.action(description="Mark selected diagnoses images as STORED_WITH_USER_PERMISSION")
    def set_retention_stored_with_permission(self, request, queryset):
        queryset.update(image_retention_status='STORED_WITH_USER_PERMISSION')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('diagnosis', 'is_helpful', 'reason', 'created_at')
    list_filter = ('is_helpful', 'reason', 'created_at')
    search_fields = ('diagnosis__id', 'reason', 'comments')
