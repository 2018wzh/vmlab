import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.users.models import Role
from apps.courses.models import Course, VirtualMachineTemplate

User = get_user_model()

class CourseAPITests(APITestCase):
    """
    课程管理API测试
    """

    @classmethod
    def setUpTestData(cls):
        """
        设置测试数据
        """
        # 创建角色
        cls.student_role, _ = Role.objects.get_or_create(name='student', defaults={'description': '学生'})
        cls.teacher_role, _ = Role.objects.get_or_create(name='teacher', defaults={'description': '教师'})
        cls.admin_role, _ = Role.objects.get_or_create(name='admin', defaults={'description': '管理员'})

        # 创建用户
        cls.student_user, _ = User.objects.get_or_create(
            username='student_test', 
            defaults={'role': cls.student_role, 'email': 'student@test.com'}
        )
        if not cls.student_user.password:
            cls.student_user.set_password('password')
            cls.student_user.save()

        cls.teacher_user, _ = User.objects.get_or_create(
            username='teacher_test',
            defaults={'role': cls.teacher_role, 'email': 'teacher@test.com'}
        )
        if not cls.teacher_user.password:
            cls.teacher_user.set_password('password')
            cls.teacher_user.save()

        cls.admin_user, _ = User.objects.get_or_create(
            username='admin_test',
            defaults={'role': cls.admin_role, 'email': 'admin@test.com', 'is_staff': True}
        )
        if not cls.admin_user.password:
            cls.admin_user.set_password('password')
            cls.admin_user.save()

        # 创建测试课程
        cls.course, _ = Course.objects.get_or_create(
            name='测试课程',
            defaults={'description': '这是一个测试课程'}
        )
        cls.course.teachers.add(cls.teacher_user)
        cls.course.students.add(cls.student_user)

    def test_teacher_can_create_course(self):
        """
        测试教师可以创建课程
        """
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('courses:course-list')
        data = {
            'name': '新课程',
            'description': '新课程描述'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.filter(name='新课程').count(), 1)

    def test_student_cannot_create_course(self):
        """
        测试学生不能创建课程
        """
        self.client.force_authenticate(user=self.student_user)
        url = reverse('courses:course-list')
        data = {
            'name': '学生课程',
            'description': '学生创建的课程'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_course_list(self):
        """
        测试获取课程列表
        """
        self.client.force_authenticate(user=self.student_user)
        url = reverse('courses:course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 学生应该只能看到自己选修的课程
        self.assertEqual(len(response.data['results']), 1)

    def test_get_course_detail(self):
        """
        测试获取课程详情
        """
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('courses:course-detail', kwargs={'pk': self.course.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.course.name)

    def test_add_student_to_course(self):
        """
        测试向课程添加学生
        """
        self.client.force_authenticate(user=self.teacher_user)
        
        # 创建一个新学生
        new_student = User.objects.create_user(
            username='new_student',
            password='password',
            role=self.student_role
        )
        
        url = reverse('courses:course-add-student', kwargs={'pk': self.course.pk})
        data = {'student_id': str(new_student.id)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.course.students.filter(id=new_student.id).exists())

    def test_remove_student_from_course(self):
        """
        测试从课程移除学生
        """
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('courses:course-remove-student', 
                     kwargs={'pk': self.course.pk, 'user_id': str(self.student_user.id)})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.course.students.filter(id=self.student_user.id).exists())

    def test_get_course_statistics(self):
        """
        测试获取课程统计信息
        """
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('courses:course-statistics', kwargs={'pk': self.course.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_students', response.data)
        self.assertIn('total_teachers', response.data)

class VirtualMachineTemplateAPITests(APITestCase):
    """
    虚拟机模板API测试
    """

    @classmethod
    def setUpTestData(cls):
        """
        设置测试数据
        """
        # 创建角色
        cls.teacher_role, _ = Role.objects.get_or_create(name='teacher', defaults={'description': '教师'})
        cls.student_role, _ = Role.objects.get_or_create(name='student', defaults={'description': '学生'})

        # 创建用户
        cls.teacher_user, _ = User.objects.get_or_create(
            username='template_teacher',
            defaults={'role': cls.teacher_role, 'email': 'template_teacher@test.com'}
        )
        if not cls.teacher_user.password:
            cls.teacher_user.set_password('password')
            cls.teacher_user.save()

        cls.student_user, _ = User.objects.get_or_create(
            username='template_student',
            defaults={'role': cls.student_role, 'email': 'template_student@test.com'}
        )
        if not cls.student_user.password:
            cls.student_user.set_password('password')
            cls.student_user.save()

        # 创建课程
        cls.course, _ = Course.objects.get_or_create(
            name='模板测试课程',
            defaults={'description': '用于测试模板的课程'}
        )
        cls.course.teachers.add(cls.teacher_user)
        cls.course.students.add(cls.student_user)

    def test_teacher_can_create_template(self):
        """
        测试教师可以创建模板
        """
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('courses:template-list')
        data = {
            'name': 'Ubuntu 20.04',
            'description': 'Ubuntu 20.04 LTS虚拟机模板',
            'file_path': '/var/lib/libvirt/images/ubuntu20.04.qcow2',
            'course': self.course.id,
            'is_public': False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(VirtualMachineTemplate.objects.filter(name='Ubuntu 20.04').count(), 1)

    def test_student_cannot_create_template(self):
        """
        测试学生不能创建模板
        """
        self.client.force_authenticate(user=self.student_user)
        url = reverse('courses:template-list')
        data = {
            'name': 'Student Template',
            'description': '学生创建的模板',
            'file_path': '/tmp/test.qcow2',
            'course': self.course.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_template_list(self):
        """
        测试获取模板列表
        """
        # 创建一个模板
        template = VirtualMachineTemplate.objects.create(
            name='Test Template',
            description='测试模板',
            file_path='/tmp/test.qcow2',
            owner=self.teacher_user,
            course=self.course,
            is_public=True
        )

        self.client.force_authenticate(user=self.student_user)
        url = reverse('courses:template-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 学生应该能看到公开模板和课程模板
        self.assertGreaterEqual(len(response.data['results']), 1)
