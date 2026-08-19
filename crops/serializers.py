from rest_framework import serializers
from .models import Crop

class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = ['id', 'name', 'name_hi', 'scientific_name', 'slug', 'icon_class', 'image', 'description', 'is_active']
