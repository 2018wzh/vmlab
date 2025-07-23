from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

def create_initial_roles_and_users(sender, **kwargs):
    """
    创建初始角色和管理员用户
    """
    Role = sender.get_model('Role')
    
    # 创建角色
    student_role, _ = Role.objects.get_or_create(name='student', defaults={'description': '学生角色'})
    teacher_role, _ = Role.objects.get_or_create(name='teacher', defaults={'description': '教师角色'})
    admin_role, _ = Role.objects.get_or_create(name='admin', defaults={'description': '管理员角色'})

    # 创建超级用户
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        admin_user.role = admin_role
        admin_user.save()
