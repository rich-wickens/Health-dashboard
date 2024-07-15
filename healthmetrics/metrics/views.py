from rest_framework import viewsets
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Smoking, Weight, Activity
from .serializers import SmokingSerializer, WeightSerializer, ActivitySerializer
from .forms import SmokingForm, WeightForm, ActivityForm
from rest_framework.permissions import IsAuthenticated
from django.contrib import messages
from django.urls import reverse
from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta

def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return render(request, 'metrics/login.html')
    else:
        if 'next' in request.GET:
            messages.info(request, 'You must be logged in to access that page.')
        return render(request, 'metrics/login.html')

@login_required
def custom_logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def home_view(request):
    # Retrieve the latest weight entry for the logged-in user
    latest_weight = Weight.objects.filter(user=request.user).order_by('-date').first()

    # Retrieve the latest smoking entry for the logged-in user
    latest_smoking = Smoking.objects.filter(user=request.user).order_by('-quit_date').first()

    # Get weekly activity totals
    start_of_week = now().date() - timedelta(days=now().date().weekday())
    end_of_week = start_of_week + timedelta(days=6)
    weekly_activities = Activity.objects.filter(user=request.user, date__range=[start_of_week, end_of_week])

    total_duration = weekly_activities.aggregate(Sum('duration'))['duration__sum'] or 0
    total_distance = weekly_activities.aggregate(Sum('distance'))['distance__sum'] or 0
    total_intensity_minutes_moderate = weekly_activities.aggregate(Sum('intensity_minutes_moderate'))['intensity_minutes_moderate__sum'] or 0
    total_intensity_minutes_vigorous = weekly_activities.aggregate(Sum('intensity_minutes_vigorous'))['intensity_minutes_vigorous__sum'] or 0

    context = {
        'latest_weight': latest_weight,
        'latest_smoking': latest_smoking,
        'total_duration': total_duration,
        'total_distance': total_distance,
        'total_intensity_minutes_moderate': total_intensity_minutes_moderate,
        'total_intensity_minutes_vigorous': total_intensity_minutes_vigorous,
        'total_intensity_minutes': total_intensity_minutes_moderate + 2 * total_intensity_minutes_vigorous,
    }

    return render(request, 'metrics/home.html', context)

class SmokingViewSet(viewsets.ModelViewSet):
    queryset = Smoking.objects.all()
    serializer_class = SmokingSerializer

@login_required
def smoking_create_view(request):
    if request.method == 'POST':
        form = SmokingForm(request.POST)
        if form.is_valid():
            smoking_instance = form.save(commit=False)
            smoking_instance.user = request.user
            form.save()
            return redirect('smoking_list')
    else:
        form = SmokingForm()
    return render(request, 'metrics/smoking/smoking_form.html', {'form': form})

@login_required
def smoking_list_view(request):
    if request.user.is_superuser:
        smokings = Smoking.objects.all()
    else:
        smokings = Smoking.objects.filter(user=request.user)
    return render(request, 'metrics/smoking/smoking_list.html', {'smokings': smokings})

@login_required
def weight_create_view(request):
    if request.method == 'POST':
        form = WeightForm(request.POST)
        if form.is_valid():
            weight_entry = form.save(commit=False)
            weight_entry.user = request.user
            weight_entry.save()
            return redirect('weight_list')
    else:
        form = WeightForm()
    return render(request, 'metrics/weight/weight_form.html', {'form': form})

@login_required
def weight_list_view(request):
    weights = Weight.objects.filter(user=request.user).order_by('-date')
    return render(request, 'metrics/weight/weight_list.html', {'weights': weights})

class WeightViewSet(viewsets.ModelViewSet):
    queryset = Weight.objects.all()
    serializer_class = WeightSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Weight.objects.all()
        return Weight.objects.filter(user=user)
    
@login_required
def activity_create_view(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity =   form.save(commit=False)
            activity.user = request.user
            activity.save()
            return redirect('home')  # Redirect to the dashboard or another page
    else:
        form = ActivityForm()
    return render(request, 'metrics/activity/activity_form.html', {'form': form})

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

@login_required
def activity_list_view(request):
    activities = Activity.objects.filter(user=request.user).order_by('-date')
    return render(request, 'metrics/activity/activity_list.html', {'activities': activities})
