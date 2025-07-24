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
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:course_id>/edit/', views.course_update, name='course_update'),
    path('courses/<int:course_id>/delete/', views.course_delete, name='course_delete'),
    # 课程成员管理
    path('courses/<int:course_id>/add_student/', views.course_add_student, name='course_add_student'),
    path('courses/<int:course_id>/remove_student/<uuid:user_id>/', views.course_remove_student, name='course_remove_student'),
    path('vms/', views.vm_list, name='vm_list'),
    path('vms/rows/', views.vm_list_partial, name='vm_list_partial'),
    path('vms/<uuid:vm_id>/', views.vm_detail, name='vm_detail'),
    path('vms/create/', views.vm_create, name='vm_create'),
    path('vms/<uuid:vm_id>/edit/', views.vm_update, name='vm_update'),
    path('vms/<uuid:vm_id>/delete/', views.vm_delete, name='vm_delete'),
    path('logout/', views.user_logout, name='logout'),
    # 用户管理
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<uuid:user_id>/edit/', views.user_update, name='user_update'),
    path('users/<uuid:user_id>/delete/', views.user_delete, name='user_delete'),
    # 用户个人信息
    path('profile/', views.user_profile, name='user_profile'),
    # 虚拟机模板管理
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/<int:template_id>/', views.template_detail, name='template_detail'),
    path('templates/<int:template_id>/delete/', views.template_delete, name='template_delete'),
]
