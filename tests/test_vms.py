"""
虚拟机管理模块测试
"""
import pytest
import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

from apps.users.models import Role, Quota
from apps.courses.models import Course, VirtualMachineTemplate
from apps.vms.models import VirtualMachine
from apps.vms.services import vm_service
from apps.vms.libvirt_manager import LibvirtManager

User = get_user_model()


class VirtualMachineModelTest(TestCase):
    """虚拟机模型测试"""
    
    def setUp(self):
        """设置测试数据"""
        # 创建角色
        self.student_role, _ = Role.objects.get_or_create(
            name='student', 
            defaults={'description': '学生'}
        )
        self.teacher_role, _ = Role.objects.get_or_create(
            name='teacher', 
            defaults={'description': '教师'}
        )
        
        # 创建用户
        self.student = User.objects.create_user(
            username='student1',
            email='student1@test.com',
            password='test123',
            role=self.student_role
        )
        
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            password='test123',
            role=self.teacher_role
        )
        
        # 创建配额
        Quota.objects.create(
            user=self.student,
            cpu_cores=8,
            memory_mb=8192,
            disk_gb=200,
            vm_limit=5
        )
        
        # 创建课程
        self.course = Course.objects.create(
            name='测试课程',
            description='测试用课程'
        )
        self.course.teachers.add(self.teacher)
        self.course.students.add(self.student)
        
        # 创建模板
        self.template = VirtualMachineTemplate.objects.create(
            name='Ubuntu',
            description='Ubuntu',
            file_path='/var/lib/libvirt/images/ubuntu.qcow2',
            owner=self.teacher,
            course=self.course
        )
    
    def test_vm_creation(self):
        """测试虚拟机创建"""
        vm = VirtualMachine.objects.create(
            name='test-vm',
            owner=self.student,
            course=self.course,
            template=self.template,
            cpu_cores=2,
            memory_mb=2048,
            disk_gb=20
        )
        
        self.assertEqual(vm.name, 'test-vm')
        self.assertEqual(vm.owner, self.student)
        self.assertEqual(vm.course, self.course)
        self.assertEqual(vm.template, self.template)
        self.assertEqual(vm.status, 'stopped')
        self.assertIsNotNone(vm.id)
    
    def test_vm_properties(self):
        """测试虚拟机属性方法"""
        vm = VirtualMachine.objects.create(
            name='test-vm',
            owner=self.student,
            course=self.course,
            template=self.template,
            cpu_cores=2,
            memory_mb=2048,
            disk_gb=20,
            status='running'
        )
        
        self.assertTrue(vm.is_running)
        self.assertFalse(vm.is_stopped)
        self.assertFalse(vm.is_paused)
        self.assertFalse(vm.can_start)
        self.assertTrue(vm.can_stop)
        self.assertTrue(vm.can_pause)
        self.assertFalse(vm.can_resume)
    
    def test_vm_status_color(self):
        """测试虚拟机状态颜色"""
        vm = VirtualMachine.objects.create(
            name='test-vm',
            owner=self.student,
            course=self.course,
            template=self.template,
            cpu_cores=2,
            memory_mb=2048,
            disk_gb=20
        )
        
        vm.status = 'running'
        self.assertEqual(vm.get_status_display_color(), 'green')
        
        vm.status = 'stopped'
        self.assertEqual(vm.get_status_display_color(), 'gray')
        
        vm.status = 'error'
        self.assertEqual(vm.get_status_display_color(), 'red')


class VirtualMachineServiceTest(TestCase):
    """虚拟机服务测试"""
    
    def setUp(self):
        """设置测试数据"""
        # 创建角色
        self.student_role, _ = Role.objects.get_or_create(
            name='student', 
            defaults={'description': '学生'}
        )
        self.teacher_role, _ = Role.objects.get_or_create(
            name='teacher', 
            defaults={'description': '教师'}
        )
        
        # 创建用户
        self.student = User.objects.create_user(
            username='student1',
            email='student1@test.com',
            password='test123',
            role=self.student_role
        )
        
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            password='test123',
            role=self.teacher_role
        )
        
        # 创建课程
        self.course = Course.objects.create(
            name='测试课程',
            description='测试用课程'
        )
        self.course.teachers.add(self.teacher)
        self.course.students.add(self.student)
        
        # 创建模板
        self.template = VirtualMachineTemplate.objects.create(
            name='Ubuntu 20.04',
            description='Ubuntu 20.04 LTS',
            file_path='/var/lib/libvirt/images/ubuntu20.04.qcow2',
            owner=self.teacher,
            course=self.course
        )
        
        # 创建虚拟机
        self.vm = VirtualMachine.objects.create(
            name='test-vm',
            owner=self.student,
            course=self.course,
            template=self.template,
            cpu_cores=2,
            memory_mb=2048,
            disk_gb=20
        )
    
    @patch('apps.vms.services.libvirt_manager')
    def test_start_vm_success(self, mock_libvirt):
        """测试启动虚拟机成功"""
        mock_libvirt.start_vm.return_value = True
        
        result = vm_service.start_vm(str(self.vm.id))
        
        self.assertTrue(result['success'])
        self.assertEqual(result['vm_id'], str(self.vm.id))
        
        # 刷新虚拟机状态
        self.vm.refresh_from_db()
        self.assertEqual(self.vm.status, 'running')
        
        mock_libvirt.start_vm.assert_called_once_with(self.vm.name)
    
    @patch('apps.vms.services.libvirt_manager')
    def test_start_vm_failure(self, mock_libvirt):
        """测试启动虚拟机失败"""
        mock_libvirt.start_vm.return_value = False
        
        result = vm_service.start_vm(str(self.vm.id))
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], '启动失败')
        
        # 刷新虚拟机状态
        self.vm.refresh_from_db()
        self.assertEqual(self.vm.status, 'error')
    
    @patch('apps.vms.services.libvirt_manager')
    def test_stop_vm_success(self, mock_libvirt):
        """测试停止虚拟机成功"""
        self.vm.status = 'running'
        self.vm.save()
        
        mock_libvirt.stop_vm.return_value = True
        
        result = vm_service.stop_vm(str(self.vm.id))
        
        self.assertTrue(result['success'])
        self.assertEqual(result['vm_id'], str(self.vm.id))
        
        # 刷新虚拟机状态
        self.vm.refresh_from_db()
        self.assertEqual(self.vm.status, 'stopped')
        
        mock_libvirt.stop_vm.assert_called_once_with(self.vm.name, force=False)
    
    @patch('apps.vms.services.libvirt_manager')
    def test_restart_vm_success(self, mock_libvirt):
        """测试重启虚拟机成功"""
        self.vm.status = 'running'
        self.vm.save()
        
        mock_libvirt.restart_vm.return_value = True
        
        result = vm_service.restart_vm(str(self.vm.id))
        
        self.assertTrue(result['success'])
        self.assertEqual(result['vm_id'], str(self.vm.id))
        
        mock_libvirt.restart_vm.assert_called_once_with(self.vm.name)
    
    @patch('apps.vms.services.libvirt_manager')
    def test_pause_vm_success(self, mock_libvirt):
        """测试暂停虚拟机成功"""
        self.vm.status = 'running'
        self.vm.save()
        
        mock_libvirt.pause_vm.return_value = True
        
        result = vm_service.pause_vm(str(self.vm.id))
        
        self.assertTrue(result['success'])
        self.assertEqual(result['vm_id'], str(self.vm.id))
        
        # 刷新虚拟机状态
        self.vm.refresh_from_db()
        self.assertEqual(self.vm.status, 'paused')
        
        mock_libvirt.pause_vm.assert_called_once_with(self.vm.name)
    
    @patch('apps.vms.services.libvirt_manager')
    def test_resume_vm_success(self, mock_libvirt):
        """测试恢复虚拟机成功"""
        self.vm.status = 'paused'
        self.vm.save()
        
        mock_libvirt.resume_vm.return_value = True
        
        result = vm_service.resume_vm(str(self.vm.id))
        
        self.assertTrue(result['success'])
        self.assertEqual(result['vm_id'], str(self.vm.id))
        
        # 刷新虚拟机状态
        self.vm.refresh_from_db()
        self.assertEqual(self.vm.status, 'running')
        
        mock_libvirt.resume_vm.assert_called_once_with(self.vm.name)
    
    @patch('apps.vms.services.libvirt_manager')
    def test_delete_vm_success(self, mock_libvirt):
        """测试删除虚拟机成功"""
        vm_id = str(self.vm.id)
        vm_name = self.vm.name
        
        mock_libvirt.delete_vm.return_value = True
        
        result = vm_service.delete_vm(vm_id)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['vm_id'], vm_id)
        
        # 验证虚拟机已从数据库删除
        with self.assertRaises(VirtualMachine.DoesNotExist):
            VirtualMachine.objects.get(id=vm_id)
        
        mock_libvirt.delete_vm.assert_called_once_with(vm_name, remove_disk=True)
    
    def test_vm_not_found(self):
        """测试虚拟机不存在"""
        fake_id = str(uuid.uuid4())
        
        result = vm_service.start_vm(fake_id)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], '虚拟机不存在')


class VirtualMachineAPITest(APITestCase):
    """虚拟机API测试"""
    
    def setUp(self):
        """设置测试数据"""
        # 创建角色
        self.student_role, _ = Role.objects.get_or_create(
            name='student', 
            defaults={'description': '学生'}
        )
        self.teacher_role, _ = Role.objects.get_or_create(
            name='teacher', 
            defaults={'description': '教师'}
        )
        self.admin_role, _ = Role.objects.get_or_create(
            name='admin', 
            defaults={'description': '管理员'}
        )
        
        # 创建用户
        self.student = User.objects.create_user(
            username='student1',
            email='student1@test.com',
            password='test123',
            role=self.student_role
        )
        
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            password='test123',
            role=self.teacher_role
        )
        
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin1@test.com',
            password='test123',
            role=self.admin_role,
            is_staff=True
        )
        
        # 创建配额
        Quota.objects.create(
            user=self.student,
            cpu_cores=8,
            memory_mb=8192,
            disk_gb=200,
            vm_limit=5
        )
        
        # 创建课程
        self.course = Course.objects.create(
            name='测试课程',
            description='测试用课程'
        )
        self.course.teachers.add(self.teacher)
        self.course.students.add(self.student)
        
        # 创建模板
        self.template = VirtualMachineTemplate.objects.create(
            name='Ubuntu 20.04',
            description='Ubuntu 20.04 LTS',
            file_path='/var/lib/libvirt/images/ubuntu20.04.qcow2',
            owner=self.teacher,
            course=self.course
        )
        
        # 创建虚拟机
        self.vm = VirtualMachine.objects.create(
            name='test-vm',
            owner=self.student,
            course=self.course,
            template=self.template,
            cpu_cores=2,
            memory_mb=2048,
            disk_gb=20
        )
        
        self.client = APIClient()
    
    def test_vm_list_as_student(self):
        """测试学生获取虚拟机列表"""
        self.client.force_authenticate(user=self.student)
        
        url = reverse('vms:vm-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 学生只能看到自己的虚拟机
        self.assertGreaterEqual(len(response.data), 1)
        # 确保返回的虚拟机都属于当前用户
        for vm_data in response.data:
            if isinstance(vm_data, dict):
                self.assertEqual(vm_data['owner'], self.student.id)
    
    def test_vm_list_as_teacher(self):
        """测试教师获取虚拟机列表"""
        self.client.force_authenticate(user=self.teacher)
        
        url = reverse('vms:vm-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 教师可以看到自己课程中学生的虚拟机
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_vm_list_as_admin(self):
        """测试管理员获取虚拟机列表"""
        self.client.force_authenticate(user=self.admin)
        
        url = reverse('vms:vm-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 管理员可以看到所有虚拟机
        self.assertGreaterEqual(len(response.data), 1)
    
    @patch('apps.vms.services.vm_service.create_vm_async')
    def test_create_vm_as_student(self, mock_create):
        """测试学生创建虚拟机"""
        self.client.force_authenticate(user=self.student)
        
        url = reverse('vms:vm-list')
        data = {
            'name': 'new-test-vm',
            'template_id': self.template.id,  # 使用整数ID
            'cpu_cores': 2,
            'memory_mb': 2048,
            'disk_gb': 20,
            'course_id': self.course.id  # 使用整数ID
        }
        
        response = self.client.post(url, data, format='json')
        
        # 如果状态码不对，打印错误信息
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'new-test-vm')
        self.assertIn('id', response.data)
        
        # 验证虚拟机已创建
        vm = VirtualMachine.objects.get(name='new-test-vm')
        self.assertEqual(vm.owner, self.student)
        self.assertEqual(vm.template, self.template)
        
        # 验证异步创建任务被调用
        mock_create.assert_called_once()
    
    def test_create_vm_without_template(self):
        """测试创建虚拟机时缺少模板"""
        self.client.force_authenticate(user=self.student)
        
        url = reverse('vms:vm-list')
        data = {
            'name': 'new-test-vm',
            'cpu_cores': 2,
            'memory_mb': 2048,
            'disk_gb': 20
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_vm_detail(self):
        """测试获取虚拟机详情"""
        self.client.force_authenticate(user=self.student)
        
        url = reverse('vms:vm-detail', kwargs={'pk': self.vm.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'test-vm')
        self.assertEqual(response.data['id'], str(self.vm.id))
    
    @patch('apps.vms.services.vm_service.start_vm')
    def test_start_vm(self, mock_start):
        """测试启动虚拟机"""
        mock_start.return_value = {'success': True, 'vm_id': str(self.vm.id)}
        
        self.client.force_authenticate(user=self.student)
        
        url = reverse('vms:vm-start', kwargs={'pk': self.vm.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        mock_start.assert_called_once_with(str(self.vm.id))
    
    @patch('apps.vms.services.vm_service.stop_vm')
    def test_stop_vm(self, mock_stop):
        """测试停止虚拟机"""
        mock_stop.return_value = {'success': True, 'vm_id': str(self.vm.id)}
        
        self.vm.status = 'running'
        self.vm.save()
        
        self.client.force_authenticate(user=self.student)
        
        url = reverse('vms:vm-stop', kwargs={'pk': self.vm.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        mock_stop.assert_called_once_with(str(self.vm.id), force=False)
    
    @patch('apps.vms.services.vm_service.restart_vm')
    def test_restart_vm(self, mock_restart):
        """测试重启虚拟机"""
        mock_restart.return_value = {'success': True, 'vm_id': str(self.vm.id)}
        
        self.vm.status = 'running'
        self.vm.save()
        
        self.client.force_authenticate(user=self.student)
        
        url = reverse('vms:vm-restart', kwargs={'pk': self.vm.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        mock_restart.assert_called_once_with(str(self.vm.id))
    
    @patch('apps.vms.services.vm_service.pause_vm')
    def test_pause_vm(self, mock_pause):
        """测试暂停虚拟机"""
        mock_pause.return_value = {'success': True, 'vm_id': str(self.vm.id)}
        
        self.vm.status = 'running'
        self.vm.save()
        
        self.client.force_authenticate(user=self.student)
        
        url = reverse('vms:vm-pause', kwargs={'pk': self.vm.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        mock_pause.assert_called_once_with(str(self.vm.id))
    
    @patch('apps.vms.services.vm_service.resume_vm')
    def test_resume_vm(self, mock_resume):
        """测试恢复虚拟机"""
        mock_resume.return_value = {'success': True, 'vm_id': str(self.vm.id)}
        
        self.vm.status = 'paused'
        self.vm.save()
        
        self.client.force_authenticate(user=self.student)
        
        url = reverse('vms:vm-resume', kwargs={'pk': self.vm.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        mock_resume.assert_called_once_with(str(self.vm.id))
    
    @patch('apps.vms.services.vm_service.delete_vm')
    def test_delete_vm(self, mock_delete):
        """测试删除虚拟机"""
        mock_delete.return_value = {'success': True, 'vm_id': str(self.vm.id)}
        
        self.client.force_authenticate(user=self.student)
        
        url = reverse('vms:vm-detail', kwargs={'pk': self.vm.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        mock_delete.assert_called_once_with(str(self.vm.id), remove_disk=True)
    
    @patch('apps.vms.libvirt_manager.libvirt_manager.get_vm_status')
    def test_vm_status(self, mock_status):
        """测试获取虚拟机状态"""
        mock_status.return_value = {
            'name': 'test-vm',
            'state': 'running',
            'vnc_port': '5900',
            'ip_address': '192.168.1.100',
            'is_active': True
        }
        
        self.client.force_authenticate(user=self.student)
        
        url = reverse('vms:vm-status', kwargs={'pk': self.vm.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], 'running')
        self.assertEqual(response.data['ip_address'], '192.168.1.100')
        
        mock_status.assert_called_once_with(self.vm.name)
    
    @patch('apps.vms.libvirt_manager.libvirt_manager.get_vm_metrics')
    def test_vm_metrics(self, mock_metrics):
        """测试获取虚拟机监控指标"""
        mock_metrics.return_value = {
            'cpu_usage': 50,
            'memory_usage': 1024,
            'memory_available': 2048,
            'disk_read': 1000,
            'disk_write': 500,
            'network_rx': 2000,
            'network_tx': 1500
        }
        
        self.client.force_authenticate(user=self.student)
        
        url = reverse('vms:vm-metrics', kwargs={'pk': self.vm.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cpu_usage'], 50)
        self.assertEqual(response.data['memory_usage'], 1024)
        
        mock_metrics.assert_called_once_with(self.vm.name)
    
    def test_vnc_console_access(self):
        """测试VNC控制台访问"""
        self.vm.status = 'running'
        self.vm.vnc_port = 5900
        self.vm.vnc_password = 'test123'
        self.vm.save()
        
        self.client.force_authenticate(user=self.student)
        
        url = reverse('vms:vm-console-vnc', kwargs={'pk': self.vm.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['vnc_port'], 5900)
        self.assertEqual(response.data['vnc_password'], 'test123')
        self.assertIn('vnc_url', response.data)
    
    def test_vnc_console_vm_not_running(self):
        """测试VNC控制台访问时虚拟机未运行"""
        self.vm.status = 'stopped'
        self.vm.save()
        
        self.client.force_authenticate(user=self.student)
        
        url = reverse('vms:vm-console-vnc', kwargs={'pk': self.vm.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_my_vms(self):
        """测试获取我的虚拟机"""
        self.client.force_authenticate(user=self.student)
        
        url = reverse('vms:vm-my-vms')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'test-vm')
    
    def test_course_vms(self):
        """测试获取课程虚拟机"""
        self.client.force_authenticate(user=self.teacher)
        
        url = reverse('vms:vm-course-vms')
        response = self.client.get(url, {'course_id': str(self.course.id)})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'test-vm')
    
    def test_permission_denied(self):
        """测试权限拒绝"""
        # 创建另一个学生
        other_student = User.objects.create_user(
            username='student2',
            email='student2@test.com',
            password='test123',
            role=self.student_role
        )
        
        self.client.force_authenticate(user=other_student)
        
        # 尝试访问其他学生的虚拟机
        url = reverse('vms:vm-detail', kwargs={'pk': self.vm.id})
        response = self.client.get(url)
        
        # 应该返回404（因为queryset中不包含其他学生的虚拟机）
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LibvirtManagerTest(TestCase):
    """Libvirt管理器测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.manager = LibvirtManager()
    
    def test_generate_mac_address(self):
        """测试生成MAC地址"""
        mac = self.manager._generate_mac_address()
        
        self.assertIsInstance(mac, str)
        self.assertTrue(mac.startswith('52:54:00'))
        self.assertEqual(len(mac.split(':')), 6)
    
    def test_generate_vm_xml(self):
        """测试生成虚拟机XML配置"""
        xml = self.manager._generate_vm_xml(
            name='test-vm',
            uuid='12345678-1234-1234-1234-123456789abc',
            memory_mb=2048,
            cpu_cores=2,
            disk_path='/path/to/disk.qcow2',
            vnc_port=5900,
            mac_address='52:54:00:12:34:56'
        )
        
        self.assertIn('<name>test-vm</name>', xml)
        self.assertIn('<memory unit=\'MiB\'>2048</memory>', xml)
        self.assertIn('<vcpu>2</vcpu>', xml)
        self.assertIn('/path/to/disk.qcow2', xml)
        self.assertIn('port=\'5900\'', xml)
        self.assertIn('52:54:00:12:34:56', xml)
    
    @patch('socket.socket')
    def test_is_port_available(self, mock_socket):
        """测试端口可用性检查"""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        # 测试端口可用
        mock_sock.connect_ex.return_value = 1
        self.assertTrue(self.manager._is_port_available(5900))
        
        # 测试端口不可用
        mock_sock.connect_ex.return_value = 0
        self.assertFalse(self.manager._is_port_available(5900))


if __name__ == '__main__':
    pytest.main([__file__])
