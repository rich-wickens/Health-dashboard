# Generated by Django 5.0.6 on 2024-09-07 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0004_alter_activity_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='strava_expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='strava_refresh_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
