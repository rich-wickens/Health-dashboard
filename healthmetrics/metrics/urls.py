from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    home_view,
    custom_login_view,
    custom_logout_view,
    smoking_create_view,
    smoking_list_view,
    smoking_edit_view,
    SmokingViewSet,
    weight_create_view,
    weight_list_view,
    weight_edit_view,
    WeightViewSet,
    activity_create_view,
    activity_list_view,
    activity_edit_view,
    ActivityViewSet,
    profile_view,
    disconnect_strava,
    strava_callback,
    fetch_strava_activities,
    signup_view,
    strava_login,
    fetch_and_print_strava_activities
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'smoking', SmokingViewSet, basename='smoking')
router.register(r'weight', WeightViewSet, basename='weight')
router.register(r'activity', ActivityViewSet, basename='activity')

api_urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

template_urlpatterns = [
    path('', home_view, name='home'),
    path('login/', custom_login_view, name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('signup/', signup_view, name='signup'),
    path('smoking/create/', smoking_create_view, name='smoking_create'),
    path('smoking/list/', smoking_list_view, name='smoking_list'),
    path('smoking/edit/<int:id>/', smoking_edit_view, name='smoking_edit'),
    path('weight/create/', weight_create_view, name='weight_create'),
    path('weight/list/', weight_list_view, name='weight_list'),
    path('weight/edit/<int:id>/', weight_edit_view, name='weight_edit'),
    path('activity/create/', activity_create_view, name='activity_create'),
    path('activity/list/', activity_list_view, name='activity_list'),
    path('activity/edit/<int:id>/', activity_edit_view, name='activity_edit'),
    path('profile/', profile_view, name='profile'),
    path('accounts/profile/disconnect_strava/', disconnect_strava, name='disconnect_strava'),
    path('accounts/', include('allauth.urls')),
    path('strava/callback/', strava_callback, name='strava_callback'),
    path('fetch-strava-activities/', fetch_strava_activities, name='fetch_strava_activities'),
    path('strava/login/', strava_login, name='strava_login'),
    path('profile/fetch-activities/', fetch_and_print_strava_activities, name='fetch_and_print_strava_activities'),
]

urlpatterns = [
    path('', include(template_urlpatterns)),
    path('api/', include(api_urlpatterns)),
    path('accounts/', include('allauth.urls')),
]