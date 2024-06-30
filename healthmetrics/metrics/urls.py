from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import smoking_create_view, smoking_list_view, SmokingViewSet, custom_login_view



# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'smoking', SmokingViewSet, basename='smoking')

api_urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

template_urlpatterns = [
    path('smoking/create/', smoking_create_view, name='smoking_create'),
    path('smoking/list/', smoking_list_view, name='smoking_list'),
    path('login/', custom_login_view, name='login'),
    # path('swagger/', TemplateView.as_view(template_name='metrics/swagger_template.html'), name='swagger-ui'),
]

urlpatterns = [
    path('', include(template_urlpatterns)),
    path('api/', include(api_urlpatterns)),
    # path('login/', custom_login_view, name='login'),
    # path('api/token/', get_jwt_token, name='get_jwt_token'),
    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]