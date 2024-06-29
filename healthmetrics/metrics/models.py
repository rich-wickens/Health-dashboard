from django.db import models

class Smoking(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    date = models.DateField()
    cigarettes_per_day = models.IntegerField()

class Diet(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    date = models.DateField()
    calories_consumed = models.IntegerField()
    fat = models.FloatField()
    protein = models.FloatField()
    carbohydrates = models.FloatField()

class Weight(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.FloatField()
    body_fat_percentage = models.FloatField()

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