import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client

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
