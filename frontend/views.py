from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from apps.courses.models import Course
from apps.vms.models import VirtualMachine


def index(request):
    return redirect('frontend:dashboard')


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('frontend:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'frontend/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('frontend:login')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('frontend:login')
    else:
        form = UserCreationForm()
    return render(request, 'frontend/register.html', {'form': form})

@login_required
def dashboard(request):
    courses = Course.objects.filter(students=request.user)
    vms = VirtualMachine.objects.filter(owner=request.user)
    return render(request, 'frontend/dashboard.html', {'courses': courses, 'vms': vms})

@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'frontend/course_list.html', {'courses': courses})

@login_required
def vm_list(request):
    vms = VirtualMachine.objects.filter(owner=request.user)
    return render(request, 'frontend/vm_list.html', {'vms': vms})
