from rest_framework import viewsets
from django.shortcuts import render
from .models import Smoking
from .serializers import SmokingSerializer

class SmokingViewSet(viewsets.ModelViewSet):
    queryset = Smoking.objects.all()
    serializer_class = SmokingSerializer
