from rest_framework import serializers
from .models import Smoking, Weight, Activity
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.contrib.auth.models import User

class SmokingSerializer(serializers.ModelSerializer):
    time_since_quit = serializers.SerializerMethodField()
    money_saved = serializers.SerializerMethodField()
    user = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)

    class Meta:
        model = Smoking
        fields = ['id', 'start_date', 'quit_date', 'cost_per_pack', 'cigarettes_per_day', 'user', 'user_id', 'time_since_quit', 'money_saved']
        extra_kwargs = {
            'start_date': {'format': '%Y-%m-%d'},
            'quit_date': {'format': '%Y-%m-%d'},
            'cost_per_pack': {'decimal_places': 2, 'max_digits': 5},
        }

    def validate(self, data):
        instance = Smoking(**data)
        try:
            instance.clean()
        except DjangoValidationError as e:
            if hasattr(e, 'message_dict'):
                raise DRFValidationError(e.message_dict)
            else:
                raise DRFValidationError(e.messages)
        return data

    def get_time_since_quit(self, obj):
        return obj.time_since_quit_breakdown()

    def get_money_saved(self, obj):
        return obj.money_saved()
    
class WeightSerializer(serializers.ModelSerializer):
    bmi = serializers.FloatField(read_only=True)
    bmi_category = serializers.SerializerMethodField()
    height = serializers.FloatField(help_text="Height in meters")
    weight = serializers.FloatField(help_text="Weight in kilograms")
    waist_circumference = serializers.FloatField(required=False, help_text="Waist circumference in CMs")
    is_waist_circumference_healthy = serializers.SerializerMethodField()

    class Meta:
        model = Weight
        fields = ['id', 'user', 'date', 'height', 'weight', 'bmi', 'ethnicity', 'bmi_category', 'waist_circumference', 'is_waist_circumference_healthy']

    def get_bmi_category(self, obj):
        return obj.get_bmi_category()
    
    def get_is_waist_circumference_healthy(self, obj):
        return obj.is_waist_circumference_healthy()
    
class ActivitySerializer(serializers.ModelSerializer):
    duration = serializers.FloatField(help_text="Duration in minutes")
    distance = serializers.FloatField(help_text="Distance in km")
    intensity_minutes_moderate = serializers.FloatField(help_text="Moderate intesity minutes")
    intensity_minutes_vigorous = serializers.FloatField(help_text="Vigorous intesity minutes")
    intensity_minutes_total = serializers.FloatField()

    class Meta:
        model = Activity
        fields = ['id', 'user', 'date', 'activity_type', 'duration', 'distance', 
                'intensity_minutes_moderate', 'intensity_minutes_vigorous', 'intensity_minutes_total']

    def get_intensity_minutes_total(self, obj):
        return obj.intensity_minutes_total()