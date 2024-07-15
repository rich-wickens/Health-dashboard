from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    home_view,
    custom_login_view,
    custom_logout_view,
    smoking_create_view,
    smoking_list_view,
    SmokingViewSet,
    weight_create_view,
    weight_list_view,
    WeightViewSet,
    activity_create_view,
    activity_list_view,
    ActivityViewSet

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
    path('smoking/create/', smoking_create_view, name='smoking_create'),
    path('smoking/list/', smoking_list_view, name='smoking_list'),
    path('weight/create/', weight_create_view, name='weight_create'),
    path('weight/list/', weight_list_view, name='weight_list'),
    path('activity/create/', activity_create_view, name='activity_create'),
    path('activity/list/', activity_list_view, name='activity_list'),
]

urlpatterns = [
    path('', include(template_urlpatterns)),
    path('api/', include(api_urlpatterns)),
]