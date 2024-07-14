from django import forms
from .models import Smoking, Weight
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class SmokingForm(forms.ModelForm):
    class Meta:
        model = Smoking
        fields = ['start_date', 'quit_date', 'cost_per_pack', 'cigarettes_per_day']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'quit_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(SmokingForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].input_formats = ['%Y-%m-%d']
        self.fields['quit_date'].input_formats = ['%Y-%m-%d']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        quit_date = cleaned_data.get('quit_date')
        cost_per_pack = cleaned_data.get('cost_per_pack')
        cigarettes_per_day = cleaned_data.get('cigarettes_per_day')

        if not start_date or not quit_date:
            raise ValidationError(_('Both start date and quit date are required.'))
        if quit_date < start_date:
            self.add_error('quit_date', _('Quit date cannot be before start date.'))
        if cost_per_pack is not None and cost_per_pack <= 0:
            self.add_error('cost_per_pack', _('Cost per pack must be greater than zero.'))
        if cigarettes_per_day is not None and cigarettes_per_day <= 0:
            self.add_error('cigarettes_per_day', _('Cigarettes per day must be greater than zero.'))

        return cleaned_data
    
class WeightForm(forms.ModelForm):
    class Meta:
        model = Weight
        fields = ['date', 'height', 'weight', 'ethnicity', 'waist_circumference']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }