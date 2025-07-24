import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
from apps.users.models import Role

pytestmark = pytest.mark.django_db
User = get_user_model()

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def admin_user():
    # 创建或获取具有 staff 权限的管理员用户
    role, _ = Role.objects.get_or_create(name='admin')
    # 确保管理员用户存在并正确设置密码和角色
    user, _ = User.objects.get_or_create(username='admin')
    user.set_password('pass12345')
    user.is_staff = True
    user.role = role
    user.save()
    return user

@pytest.fixture
def normal_user():
    # 创建或获取普通用户
    role, _ = Role.objects.get_or_create(name='student')
    # 确保普通用户存在并正确设置密码和角色
    user, _ = User.objects.get_or_create(username='user1')
    user.set_password('pass12345')
    user.is_staff = False
    user.role = role
    user.save()
    return user

def test_user_list_requires_login(client):
    url = reverse('frontend:user_list')
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('frontend:login') in response.url

def test_user_list_shows_users(client, admin_user):
    client.force_login(admin_user)
    url = reverse('frontend:user_list')
    response = client.get(url)
    assert response.status_code == 200
    assert b'user1' in response.content or b'admin' in response.content

def test_user_create_view_and_creates_user(client, admin_user):
    client.force_login(admin_user)
    url = reverse('frontend:user_create')
    response = client.get(url)
    assert response.status_code == 200
    data = {
        'username': 'newuser',
        'first_name': 'New',
        'last_name': 'User',
        'email': 'new@example.com',
        'role': admin_user.role.pk,
        'is_active': True,
        'is_staff': False,
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert User.objects.filter(username='newuser').exists()

def test_user_update_view_and_updates_user(client, admin_user, normal_user):
    client.force_login(admin_user)
    url = reverse('frontend:user_update', args=[normal_user.pk])
    response = client.get(url)
    assert response.status_code == 200
    data = {
        'username': 'user1',
        'first_name': 'Updated',
        'last_name': 'Name',
        'email': 'updated@example.com',
        'role': normal_user.role.pk,
        'is_active': False,
        'is_staff': False,
    }
    response = client.post(url, data)
    assert response.status_code == 302
    normal_user.refresh_from_db()
    assert normal_user.first_name == 'Updated'
    assert not normal_user.is_active

def test_user_delete_view_and_deletes_user(client, admin_user, normal_user):
    client.force_login(admin_user)
    url = reverse('frontend:user_delete', args=[normal_user.pk])
    response = client.post(url)
    assert response.status_code == 302
    assert not User.objects.filter(pk=normal_user.pk).exists()
