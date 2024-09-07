import requests
import logging
from rest_framework import viewsets
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .models import Smoking, Weight, Activity, Profile
from .serializers import SmokingSerializer, WeightSerializer, ActivitySerializer
from .forms import SmokingForm, WeightForm, ActivityForm, UserForm, ProfileForm, SignupForm
from rest_framework.permissions import IsAuthenticated
from django.contrib import messages
from django.urls import reverse
from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta, datetime, timezone
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.strava.views import StravaOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView, OAuth2CallbackView
from django.http import JsonResponse

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
def smoking_edit_view(request, id):
    smoking = get_object_or_404(Smoking, id=id)
    if request.method == 'POST':
        form = SmokingForm(request.POST, instance=smoking)
        if form.is_valid():
            form.save()
            return redirect('smoking_list')
    else:
        form = SmokingForm(instance=smoking)
    
    return render(request, 'metrics/smoking/smoking_edit.html', {'form': form})

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
def weight_edit_view(request, id):
    weight = get_object_or_404(Weight, id=id)
    if request.method == 'POST':
        form = WeightForm(request.POST, instance=weight)
        if form.is_valid():
            form.save()
            return redirect('weight_list')
    else:
        form = WeightForm(instance=weight)
    
    return render(request, 'metrics/weight/weight_edit.html', {'form': form})
    
@login_required
def activity_create_view(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity =   form.save(commit=False)
            activity.user = request.user
            activity.duration = form.cleaned_data['duration']
            activity.save()
            return redirect('home')
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

class StravaLogin(OAuth2LoginView):
    adapter_class = StravaOAuth2Adapter
    callback_url = 'http://127.0.0.1:8000/accounts/strava/callback/' 
    client_class = OAuth2Client

class StravaCallback(OAuth2CallbackView):
    adapter_class = StravaOAuth2Adapter
    client_class = OAuth2Client


def strava_login(request):
    return StravaLogin.as_view()(request)

@login_required
def activity_edit_view(request, id):
    activity = get_object_or_404(Activity, id=id)
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            return redirect('activity_list')
    else:
        form = ActivityForm(instance=activity)
    
    return render(request, 'metrics/activity/activity_edit.html', {'form': form})

# Sign up view
def signup_view(request):
    if request.method == 'POST':
        user_form = SignupForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # Set backend attribute for the user
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return redirect('home')
    else:
        user_form = SignupForm()
        profile_form = ProfileForm()
    return render(request, 'metrics/signup.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def profile_view(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)
    strava_connected = SocialAccount.objects.filter(user=user, provider='strava').exists()

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'strava_connected': strava_connected,
    }
    return render(request, 'metrics/profile.html', context)

# Disconnect Strava view
@login_required
def disconnect_strava(request):
    user = request.user
    try:
        social_account = SocialAccount.objects.get(user=user, provider='strava')
        social_account.delete()
        user.profile.strava_connected = False
        user.profile.strava_access_token = ''
        user.profile.save()
    except ObjectDoesNotExist:
        pass
    return redirect('profile')

# Strava callback view
@login_required
def strava_callback(request):
    code = request.GET.get('code')
    if not code:
        return JsonResponse({'error': 'Missing code in the callback'}, status=400)

    client_id = settings.SOCIALACCOUNT_PROVIDERS['strava']['APP']['client_id']
    client_secret = settings.SOCIALACCOUNT_PROVIDERS['strava']['APP']['secret']

    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
    )

    token_data = response.json()

    # Log the token data for debugging
    logger.debug("Token Data from Strava: %s", token_data)

    if 'access_token' in token_data:
        # Save tokens
        access_token = token_data['access_token']
        refresh_token = token_data['refresh_token']
        expires_at = datetime.utcfromtimestamp(token_data['expires_at']).replace(tzinfo=timezone.utc)

        # Get or create the social account and token
        social_app = SocialApp.objects.get(provider='strava')
        social_account, created = SocialAccount.objects.get_or_create(user=request.user, provider='strava')
        social_token, created = SocialToken.objects.get_or_create(account=social_account, app=social_app)
        
        social_token.token = access_token
        social_token.token_secret = refresh_token
        social_token.expires_at = expires_at
        social_token.save()

        # Save to profile (if you have a Profile model)
        profile = request.user.profile
        profile.strava_access_token = access_token
        profile.strava_refresh_token = refresh_token
        profile.strava_expires_at = expires_at
        profile.save()

        return redirect('profile')
    else:
        logger.error("Failed to fetch access token from Strava: %s", token_data)
        return JsonResponse({'error': 'Failed to fetch access token from Strava', 'details': token_data}, status=400)
    # token_data = response.json()
    # if 'access_token' in token_data:
    #     access_token = token_data['access_token']
    #     # Save the access token to the user's profile
    #     request.user.profile.strava_access_token = access_token
    #     request.user.profile.strava_connected = True
    #     request.user.profile.save()
    #     return redirect('profile')
    # else:
    #     return render(request, 'error.html', {'message': 'Authentication with Strava failed.'})

# Fetch Strava activities view
@login_required
def fetch_strava_activities(request):
    access_token = request.user.profile.strava_access_token
    response = requests.get(
        'https://www.strava.com/api/v3/athlete/activities',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    activities = response.json()

    # Process and save activities to your database
    for activity in activities:
        Activity.objects.create(
            user=request.user,
            date=activity['start_date'],
            activity_type=activity['type'].lower(),
            duration=activity['elapsed_time'] / 60,  # Convert to minutes
            distance=activity['distance'] / 1000,  # Convert to kilometers
            intensity_minutes_moderate=activity.get('average_speed', 0),  # Example, update based on actual data
            intensity_minutes_vigorous=activity.get('average_speed', 0) * 2  # Example, update based on actual data
        )

    return redirect('profile')

#debug function
@login_required
def fetch_and_print_strava_activities(request):
    access_token = request.user.profile.strava_access_token
    response = requests.get(
        'https://www.strava.com/api/v3/athlete/activities',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    activities = response.json()
    print(activities)  # Print activities to the console for debugging

    return JsonResponse({'activities': activities})  # Return activities as JSON
