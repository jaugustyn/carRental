from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from .views import *

router = DefaultRouter()
router.register(r'cars', CarViewSet, basename="cars")

urlpatterns = [
    path('openapi', get_schema_view(
        title="Car Rental",
        description="API",
        version="1.0.0"
    ), name='openapi-schema'),
    path('', TemplateView.as_view(template_name='swagger-ui.html', extra_context={'schema_url': 'openapi-schema'}), name='swagger-ui'),
    path('', include(router.urls)),
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),

]
