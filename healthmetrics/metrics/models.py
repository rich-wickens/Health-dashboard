from django.db import models
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import calendar

class Smoking(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    start_date = models.DateField()
    quit_date = models.DateField()
    cost_per_pack = models.DecimalField(max_digits=5, decimal_places=2)
    cigarettes_per_day = models.IntegerField()

    def __str__(self):
        # String representation of the model instance
        return f"{self.user.username} - Quit on {self.quit_date}"
        
    def clean(self):
        if self.start_date is None or self.quit_date is None:
            raise ValidationError(_('Start date and quit date are required.'))
        if self.quit_date < self.start_date:
            raise ValidationError(_('Quit date cannot be before start date.'))
        if self.cost_per_pack <= 0:
            raise ValidationError(_('Cost per pack must be greater than zero.'))
        if self.cigarettes_per_day <= 0:
            raise ValidationError(_('Cigarettes per day must be greater than zero.'))
        if self.start_date > timezone.now().date():
            raise ValidationError(_('Start date cannot be in the future.'))
        if self.quit_date > timezone.now().date():
            raise ValidationError(_('Quit date cannot be in the future.'))
        
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def time_since_quit(self):
        # Calculate the time difference in days between now and the quit date
        now = timezone.now().date()
        time_diff = now - self.quit_date
        return time_diff
    
    def time_since_quit_breakdown(self):
        # Get the current datetime with timezone information
        now = timezone.now()
        # Combine quit date with minimum time (00:00:00) and make it timezone-aware
        quit_datetime = datetime.combine(self.quit_date, datetime.min.time())
        quit_datetime = timezone.make_aware(quit_datetime, timezone.get_default_timezone())
        # Calculate the time difference between now and the quit datetime
        time_diff = now - quit_datetime

        # Total seconds since quitting
        total_seconds = time_diff.total_seconds()
        # Total minutes since quitting
        total_minutes = total_seconds / 60
        # Total days since quitting
        total_days = time_diff.days
        # Total months since quitting (approximation)
        total_months = (total_days // 30)
        # Total years since quitting (approximation)
        total_years = (total_days // 365)

        # Calculate precise years, months, and days
        quit_year = self.quit_date.year
        current_year = now.year
        years = current_year - quit_year

        quit_month = self.quit_date.month
        current_month = now.month
        months = current_month - quit_month
        # Adjust if months are negative
        if months < 0:
            years -= 1
            months += 12

        quit_day = self.quit_date.day
        current_day = now.day
        days = current_day - quit_day
        # Adjust if days are negative
        if days < 0:
            months -= 1
            previous_month = current_month - 1 if current_month > 1 else 12
            days_in_prev_month = calendar.monthrange(now.year, previous_month)[1]
            days += days_in_prev_month

        # If months go negative after day adjustment, correct the year and month
        if months < 0:
            years -= 1
            months += 12

        # Calculate hours, minutes, and seconds from the total seconds
        hours, remaining_seconds = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remaining_seconds, 60)

        return {
            # Breakdown including years, months, days, hours, minutes, and seconds
            'years_months_days_hours_minutes_seconds': {
                'years': years,
                'months': months,
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds
            },
            # Breakdown including months, days, hours, minutes, and seconds
            'months_days_hours_minutes_seconds': {
                'months': total_months,
                'days': total_days % 30,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds
            },
            # Breakdown including days, hours, minutes, and seconds
            'days_hours_minutes_seconds': {
                'days': total_days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds
            },
            # Breakdown including total minutes and remaining seconds
            'minutes_seconds': {
                'minutes': total_minutes,
                'seconds': total_seconds % 60
            },
            # Total seconds since quitting
            'seconds': total_seconds
        }
    
    def money_saved(self):
        # Calculate the total number of days since quitting
        days_quit = self.time_since_quit().days
        # Calculate the number of packs per day
        packs_per_day = Decimal(self.cigarettes_per_day) / Decimal(20)
        # Calculate the money saved based on days quit, packs per day, and cost per pack
        money_saved = Decimal(days_quit) * packs_per_day * self.cost_per_pack
        return money_saved
    

class Diet(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    date = models.DateField()
    calories_consumed = models.IntegerField()
    fat = models.FloatField()
    protein = models.FloatField()
    carbohydrates = models.FloatField()

class Weight(models.Model):
    ASIAN = 'Asian'
    BLACK = 'Black'
    MIDDLE_EASTERN = 'Middle Eastern'
    MIXED = 'Mixed'
    WHITE = 'White'
    OTHER = 'Other'
    PREFER_NOT_TO_SAY = 'Prefer not to say'

    ETHNICITY_CHOICES = [
        (ASIAN, 'Asian or Asian British'),
        (BLACK, 'Black, African, Caribbean or Black British'),
        (MIDDLE_EASTERN, 'Middle Eastern'),
        (MIXED, 'Mixed or multiple ethnicities with an Asian, Black or Middle Eastern background'),
        (WHITE, 'White'),
        (OTHER, 'Other ethnic group'),
        (PREFER_NOT_TO_SAY, 'Prefer not to say'),
    ]

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    date = models.DateField()
    height = models.FloatField()  # height in meters 
    weight = models.FloatField()  # weight in kilograms
    bmi = models.FloatField(blank=True, null=True)
    ethnicity = models.CharField(max_length=50, choices=ETHNICITY_CHOICES, default=PREFER_NOT_TO_SAY)
    waist_circumference = models.FloatField(null=True, blank=True) # waist circumferance in CMs

    def save(self, *args, **kwargs):
        self.clean()
        self.bmi = self.calculate_bmi()
        super().save(*args, **kwargs)

    def clean(self):
        if self.height <= 0:
            raise ValidationError(_('Height must be greater than zero.'))
        if self.weight <= 0:
            raise ValidationError(_('Weight must be greater than zero.'))
        if self.ethnicity not in dict(self.ETHNICITY_CHOICES):
            raise ValidationError(_('Invalid ethnicity choice.'))

    def calculate_bmi(self):
        if self.height > 0:
            return self.weight / (self.height ** 2)
        return None

    def get_bmi_category(self):
        bmi = self.calculate_bmi()
        if bmi is None:
            return 'Invalid BMI'

        if self.ethnicity in [self.ASIAN, self.BLACK, self.MIDDLE_EASTERN, self.MIXED]:
            if bmi < 18.5:
                return 'Underweight'
            elif bmi < 23:
                return 'Healthy'
            elif bmi < 27.5:
                return 'Overweight'
            else:
                return 'Obese'
        else:  # WHITE, OTHER, PREFER_NOT_TO_SAY
            if bmi < 18.5:
                return 'Underweight'
            elif bmi < 25:
                return 'Healthy'
            elif bmi < 30:
                return 'Overweight'
            else:
                return 'Obese'
            
    def is_waist_circumference_healthy(self):
        if self.waist_circumference is not None and self.height > 0:
            return self.waist_circumference < (self.height * 50) # height in meters, waist circumference in cms
        return None

    def __str__(self):
        return f"{self.user.username} - {self.date} - BMI: {self.bmi:.2f} - {self.get_bmi_category()}"

class Activity(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    date = models.DateField()
    steps = models.IntegerField()
    distance_km = models.FloatField()
    active_minutes = models.IntegerField()

class ResistanceTraining(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    date = models.DateField()
    exercise_name = models.CharField(max_length=100)
    sets = models.IntegerField()
    reps = models.IntegerField()
    weight_kg = models.FloatField()

class CoffeeDrinking(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    date = models.DateField()
    cups_per_day = models.IntegerField()