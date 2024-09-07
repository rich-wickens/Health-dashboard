from celery import shared_task
from django.utils import timezone
from django.conf import settings
import requests
from .models import Activity
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

@shared_task
def fetch_strava_activities():
    # Fetch Strava activities for all users connected to Strava
    from allauth.socialaccount.models import SocialToken, SocialAccount

    strava_provider = 'strava'
    social_accounts = SocialAccount.objects.filter(provider=strava_provider)

    all_activities = []

    for account in social_accounts:
        token = SocialToken.objects.get(account=account, account__provider=strava_provider).token
        response = requests.get(
            'https://www.strava.com/api/v3/athlete/activities',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        activities = response.json()
        all_activities.append(activities)

        # Log the data for inspection
        logger.info(f"Fetched activities for user {account.user}: {activities}")

        # Process and save activities to your database
        for activity in activities:
            Activity.objects.create(
                user=account.user,
                date=activity['start_date'],
                activity_type=activity['type'].lower(),
                duration=activity['elapsed_time'] / 60,  # Convert to minutes
                distance=activity['distance'] / 1000,  # Convert to kilometers
                intensity_minutes_moderate=activity.get('average_speed', 0),  # Example, update based on actual data
                intensity_minutes_vigorous=activity.get('average_speed', 0) * 2  # Example, update based on actual data
            )
    
    return all_activities

    # profiles = Profile.objects.filter(strava_connected=True)
    # for profile in profiles:
    #     access_token = profile.strava_access_token
    #     if not access_token:
    #         continue

    #     response = requests.get(
    #         'https://www.strava.com/api/v3/athlete/activities',
    #         headers={'Authorization': f'Bearer {access_token}'}
    #     )

    #     if response.status_code == 200:
    #         activities = response.json()
    #         for activity in activities:
    #             activity_id = activity['id']
    #             if not Activity.objects.filter(strava_activity_id=activity_id).exists():
    #                 Activity.objects.create(
    #                     user=profile.user,
    #                     strava_activity_id=activity_id,
    #                     date=activity['start_date'],
    #                     activity_type=activity['type'].lower(),
    #                     duration=activity['elapsed_time'] / 60,  # Convert to minutes
    #                     distance=activity['distance'] / 1000,  # Convert to kilometers
    #                     intensity_minutes_moderate=activity.get('average_speed', 0),  # Example, update based on actual data
    #                     intensity_minutes_vigorous=activity.get('average_speed', 0) * 2  # Example, update based on actual data
    #                 )