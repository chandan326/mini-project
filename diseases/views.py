from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from .models import Disease, Symptom
from .serializers import DiseaseSerializer, SymptomSerializer

def disease_list_view(request):
    diseases = Disease.objects.filter(active=True).select_related('crop')
    return render(request, 'diseases/disease_list.html', {'diseases': diseases})

def disease_detail_view(request, pk):
    disease = get_object_or_404(Disease, pk=pk, active=True)
    knowledge = getattr(disease, 'knowledge_source', None)
    return render(request, 'diseases/disease_detail.html', {'disease': disease, 'knowledge': knowledge})

class DiseaseListAPIView(generics.ListAPIView):
    serializer_class = DiseaseSerializer
    
    def get_queryset(self):
        queryset = Disease.objects.filter(active=True).select_related('crop').prefetch_related('symptoms')
        crop_id = self.request.query_params.get('crop_id')
        if crop_id:
            queryset = queryset.filter(crop_id=crop_id)
        return queryset

class DiseaseDetailAPIView(generics.RetrieveAPIView):
    queryset = Disease.objects.filter(active=True)
    serializer_class = DiseaseSerializer
