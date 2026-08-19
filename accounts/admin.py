from django.contrib import admin
from .models import FarmerProfile

@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'location_region', 'preferred_language', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'phone_number', 'location_region')
