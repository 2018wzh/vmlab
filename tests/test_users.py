import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.users.models import Role, Quota

User = get_user_model()

class UserAPITests(APITestCase):
    """
    用户管理API测试
    """

    @classmethod
    def setUpTestData(cls):
        """
        设置测试数据
        """
        # 创建或获取角色
        cls.student_role, _ = Role.objects.get_or_create(name='student', defaults={'description': '学生'})
        cls.teacher_role, _ = Role.objects.get_or_create(name='teacher', defaults={'description': '教师'})
        cls.admin_role, _ = Role.objects.get_or_create(name='admin', defaults={'description': '管理员'})

        # 创建或获取用户
        cls.student_user, _ = User.objects.get_or_create(username='student', defaults={'role': cls.student_role})
        if not cls.student_user.password:
            cls.student_user.set_password('password')
            cls.student_user.save()

        cls.admin_user, created = User.objects.get_or_create(
            username='admin', 
            defaults={'email': 'admin@test.com', 'role': cls.admin_role, 'is_staff': True, 'is_superuser': True}
        )
        if created:
            cls.admin_user.set_password('password')
            cls.admin_user.save()
        
        # 为用户创建或获取配额
        Quota.objects.get_or_create(user=cls.student_user)
        Quota.objects.get_or_create(user=cls.admin_user)


    def test_user_registration(self):
        """
        测试用户注册
        """
        url = reverse('users:user_register')
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'newpassword123',
            'password2': 'newpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3) # admin, student, newuser
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.role.name, 'student') # 验证默认角色
        self.assertTrue(Quota.objects.filter(user=new_user).exists()) # 验证默认配额创建

    def test_user_login(self):
        """
        测试用户登录获取JWT Token
        """
        url = reverse('users:token_obtain_pair')
        data = {'username': 'student', 'password': 'password'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_get_user_profile(self):
        """
        测试获取当前登录用户的个人信息
        """
        url = reverse('users:user_profile')
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.student_user.username)

    def test_admin_can_list_users(self):
        """
        测试管理员可以获取用户列表
        """
        url = reverse('users:user-list')
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2) # admin, student

    def test_student_cannot_list_users(self):
        """
        测试非管理员用户不能获取用户列表
        """
        url = reverse('users:user-list')
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_user_quota(self):
        """
        测试管理员可以更新用户配额
        """
        url = reverse('users:user-quota', kwargs={'pk': self.student_user.pk})
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'cpu_cores': 8,
            'memory_mb': 8192,
            'disk_gb': 200,
            'vm_limit': 10
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student_user.quota.refresh_from_db()
        self.assertEqual(self.student_user.quota.cpu_cores, 8)

    def test_admin_can_assign_role(self):
        """
        测试管理员可以分配角色
        """
        url = reverse('users:user-roles', kwargs={'pk': self.student_user.pk})
        self.client.force_authenticate(user=self.admin_user)
        data = {'role_id': self.teacher_role.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.role, self.teacher_role)
