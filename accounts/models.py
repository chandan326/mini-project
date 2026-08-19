from django.db import models
from django.contrib.auth.models import User

class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    location_region = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Punjab, Maharashtra, Uttar Pradesh")
    preferred_language = models.CharField(max_length=10, choices=[('en', 'English'), ('hi', 'Hindi')], default='en')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Farmer Profile for {self.user.username}"
