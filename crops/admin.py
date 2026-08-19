from django.contrib import admin
from .models import Crop

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_hi', 'scientific_name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'name_hi', 'scientific_name')
    prepopulated_fields = {'slug': ('name',)}
