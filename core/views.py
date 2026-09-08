from django.shortcuts import render
from crops.models import Crop
from diseases.models import Disease
from django.db.models import Count, Q

def home_view(request):
    """Landing Home Page with Hero, Steps, Crops Grid, and Safety Disclaimer."""
    crops = Crop.objects.filter(is_active=True).annotate(disease_count=Count('diseases', filter=Q(diseases__active=True)))
    diseases_count = Disease.objects.filter(active=True).count()
    context = {
        'crops': crops,
        'diseases_count': diseases_count,
    }
    return render(request, 'home.html', context)

def about_view(request):
    """About Platform & Methodology Page."""
    return render(request, 'about.html')

def how_it_works_view(request):
    """Detailed How It Works Explanation Page."""
    return render(request, 'how_it_works.html')
