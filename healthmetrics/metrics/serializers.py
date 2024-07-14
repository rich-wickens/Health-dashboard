from rest_framework import serializers
from .models import Smoking, Weight
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

    class Meta:
        model = Weight
        fields = ['id', 'user', 'date', 'height', 'weight', 'bmi', 'ethnicity', 'bmi_category']

    def get_bmi_category(self, obj):
        return obj.get_bmi_category()