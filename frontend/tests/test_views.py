import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
from apps.courses.models import Course
from apps.vms.models import VirtualMachine
import uuid

pytestmark = pytest.mark.django_db

User = get_user_model()

@pytest.fixture
def client():
    return Client()

def test_login_page_access(client):
    url = reverse('frontend:login')
    response = client.get(url)
    assert response.status_code == 200
    assert b'<form' in response.content

def test_login_redirects_dashboard(client):
    user = User.objects.create_user(username='testuser', password='pass12345')
    url = reverse('frontend:login')
    response = client.post(url, {'username': 'testuser', 'password': 'pass12345'})
    assert response.status_code == 302
    assert response.url == reverse('frontend:dashboard')

def test_dashboard_requires_login(client):
    url = reverse('frontend:dashboard')
    response = client.get(url)
    # Redirect to login because not authenticated
    assert response.status_code == 302
    assert reverse('frontend:login') in response.url

def test_register_page_access(client):
    url = reverse('frontend:register')
    response = client.get(url)
    assert response.status_code == 200
    assert b'<form' in response.content

def test_user_registration(client):
    url = reverse('frontend:register')
    data = {
        'username': 'newuser',
        'password1': 'pass12345',
        'password2': 'pass12345'
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('frontend:login')
    assert User.objects.filter(username='newuser').exists()

def test_dashboard_shows_sections(client):
    user = User.objects.create_user(username='testuser2', password='pass12345')
    client.login(username='testuser2', password='pass12345')
    url = reverse('frontend:dashboard')
    response = client.get(url)
    assert response.status_code == 200
    assert b'My Courses' in response.content
    assert b'My Virtual Machines' in response.content

def test_course_list_requires_login(client):
    url = reverse('frontend:course_list')
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('frontend:login') in response.url

def test_vm_list_requires_login(client):
    url = reverse('frontend:vm_list')
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('frontend:login') in response.url

def test_course_detail_requires_login(client):
    url = reverse('frontend:course_detail', args=[1])
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('frontend:login') in response.url

def test_course_detail_shows_info(client):
    # 创建用户并登录
    user = User.objects.create_user(username='courseuser', password='pass12345')
    client.login(username='courseuser', password='pass12345')
    # 创建课程
    course = Course.objects.create(name='TestCourse', description='CourseDesc')
    url = reverse('frontend:course_detail', args=[course.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert b'TestCourse' in response.content
    assert b'CourseDesc' in response.content

def test_vm_detail_requires_login(client):
    sample_uuid = uuid.uuid4()
    url = reverse('frontend:vm_detail', args=[sample_uuid])
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('frontend:login') in response.url

def test_vm_detail_shows_info(client):
    # 创建用户并登录
    user = User.objects.create_user(username='vmuser', password='pass12345')
    client.login(username='vmuser', password='pass12345')
    # 创建虚拟机
    vm = VirtualMachine.objects.create(
        name='TestVM', owner=user, cpu_cores=2, memory_mb=1024, disk_gb=20
    )
    url = reverse('frontend:vm_detail', args=[vm.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert b'TestVM' in response.content
    assert '状态'.encode('utf-8') in response.content
    assert b'2 cores' in response.content
    assert b'1024 MB' in response.content
    assert b'20 GB' in response.content
