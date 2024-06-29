from rest_framework import serializers
from .models import Smoking
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

class SmokingSerializer(serializers.ModelSerializer):
    time_since_quit = serializers.SerializerMethodField()
    money_saved = serializers.SerializerMethodField()

    class Meta:
        model = Smoking
        fields = '__all__'

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