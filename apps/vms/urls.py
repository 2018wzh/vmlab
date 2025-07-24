"""
虚拟机管理URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'vms'

router = DefaultRouter()
router.register(r'vms', views.VirtualMachineViewSet, basename='vm')

urlpatterns = [
    path('', include(router.urls)),
]
