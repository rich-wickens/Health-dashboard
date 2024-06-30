from django import forms
from .models import Smoking
from django.core.exceptions import ValidationError

class SmokingForm(forms.ModelForm):
    class Meta:
        model = Smoking
        fields = ['start_date', 'quit_date', 'cost_per_pack', 'cigarettes_per_day']

    def clean(self):
        cleaned_data = super().clean()
        try:
            self.instance.clean()
        except ValidationError as e:
            self.add_error(None, e)
        return cleaned_data