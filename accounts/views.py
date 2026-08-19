from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import FarmerRegistrationForm
from .models import FarmerProfile
from diagnosis.models import Diagnosis

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = FarmerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            FarmerProfile.objects.create(
                user=user,
                phone_number=form.cleaned_data.get('phone_number'),
                location_region=form.cleaned_data.get('location_region')
            )

            login(request, user)
            messages.success(request, f"Welcome to AgriHealth AI, {user.first_name or user.username}!")
            return redirect('dashboard')
    else:
        form = FarmerRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Signed in successfully as {user.username}.")
            next_url = request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have logged out.")
    return redirect('home')

@login_required
def dashboard_view(request):
    """Farmer Dashboard listing metrics and past plant health diagnoses."""
    user_diagnoses = Diagnosis.objects.filter(user=request.user).select_related('crop', 'predicted_disease')
    
    total_count = user_diagnoses.count()
    low_risk_count = user_diagnoses.filter(predicted_disease__severity='LOW').count()
    disease_count = user_diagnoses.exclude(predicted_disease__severity='LOW').count()
    recent_diagnoses = user_diagnoses[:10]

    context = {
        'total_count': total_count,
        'low_risk_count': low_risk_count,
        'disease_count': disease_count,
        'recent_diagnoses': recent_diagnoses
    }
    return render(request, 'accounts/dashboard.html', context)
