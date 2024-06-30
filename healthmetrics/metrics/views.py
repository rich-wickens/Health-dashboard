from rest_framework import viewsets
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, AnonymousUser
from .models import Smoking
from .serializers import SmokingSerializer
from .forms import SmokingForm
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

def custom_login_view(request):
    """
    Custom login view to authenticate the user and obtain JWT tokens.
    Stores the tokens in cookies upon successful authentication.
    """
    if request.method == 'POST':
        # Get username and password from POST data
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log in the user
            login(request, user)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            # Create a response and set cookies for access and refresh tokens
            response = redirect('smoking_list')
            response.set_cookie('access_token', str(refresh.access_token), httponly=True)
            response.set_cookie('refresh_token', str(refresh), httponly=True)

            # Debugging: print cookies set in the response
            print("Access Token Cookie:", response.cookies['access_token'])
            print("Refresh Token Cookie:", response.cookies['refresh_token'])

            return response
        else:
            # Render login page with error message if authentication fails
            return render(request, 'metrics/login.html', {'error': 'Invalid credentials'})
    else:
        # Render login page for GET request
        return render(request, 'metrics/login.html')

class SmokingViewSet(viewsets.ModelViewSet):
    queryset = Smoking.objects.all()
    serializer_class = SmokingSerializer

def smoking_create_view(request):
    if request.method == 'POST':
        form = SmokingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('smoking_list')
    else:
        form = SmokingForm()
    return render(request, 'metrics/smoking_form.html', {'form': form})

def smoking_list_view(request):
    user_id = request.GET.get('user_id')
    if user_id:
        smokings = Smoking.objects.filter(user_id=user_id)
        return render(request, 'metrics/smoking_list.html', {'smokings': smokings})
    return render(request, 'metrics/smoking_list.html', {'error': 'User ID is required'})
