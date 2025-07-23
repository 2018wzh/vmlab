from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CourseViewSet, VirtualMachineTemplateViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'templates', VirtualMachineTemplateViewSet, basename='template')

app_name = 'courses'

urlpatterns = [
    path('', include(router.urls)),
]
