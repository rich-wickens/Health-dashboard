from celery import shared_task
import requests
from .models import Activity

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

        # Process and save activities to the database
        for activity in activities:
            Activity.objects.create(
                user=account.user,
                date=activity['start_date'],
                activity_type=activity['type'].lower(),
                duration=activity['elapsed_time'] / 60,  # Convert to minutes
                distance=activity['distance'] / 1000,  # Convert to kilometers
                intensity_minutes_moderate=activity.get('heartrate_mins_easy', 0),  
                intensity_minutes_vigorous=activity.get('heartrate_mins_hard', 0) * 2 
            )
    
    return all_activities