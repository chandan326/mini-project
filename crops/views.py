from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from .models import Crop
from .serializers import CropSerializer

def crop_list_view(request):
    crops = Crop.objects.filter(is_active=True)
    return render(request, 'crops/crop_list.html', {'crops': crops})

def crop_detail_view(request, slug):
    crop = get_object_or_404(Crop, slug=slug, is_active=True)
    diseases = crop.diseases.filter(active=True)
    return render(request, 'crops/crop_detail.html', {'crop': crop, 'diseases': diseases})

class CropListAPIView(generics.ListAPIView):
    queryset = Crop.objects.filter(is_active=True)
    serializer_class = CropSerializer

class CropDetailAPIView(generics.RetrieveAPIView):
    queryset = Crop.objects.filter(is_active=True)
    serializer_class = CropSerializer
    lookup_field = 'slug'
