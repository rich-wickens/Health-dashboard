from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        # Ensure this method is only used for new social logins
        if sociallogin.is_existing:
            return
        # Check if a user is already logged in
        if request.user.is_authenticated:
            # Get the current logged-in user
            current_user = request.user
            # Check if a SocialAccount already exists for this user and provider
            try:
                existing_account = SocialAccount.objects.get(user=current_user, provider=sociallogin.account.provider)
                # Update the sociallogin object to associate with the existing account
                sociallogin.account = existing_account
            except SocialAccount.DoesNotExist:
                # Associate the social account with the currently logged-in user
                sociallogin.connect(request, current_user)
        else:
            # If no user is logged in, do nothing
            pass
