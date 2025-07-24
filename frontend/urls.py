from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('vms/', views.vm_list, name='vm_list'),
    path('vms/<uuid:vm_id>/', views.vm_detail, name='vm_detail'),
    path('logout/', views.user_logout, name='logout'),
]
