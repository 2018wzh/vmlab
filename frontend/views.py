from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
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
    """User registration using custom user creation form."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('frontend:login')
    else:
        form = CustomUserCreationForm()
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
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = course.students.all()
    teachers = course.teachers.all()
    return render(request, 'frontend/course_detail.html', {
        'course': course,
        'students': students,
        'teachers': teachers,
    })

@login_required
def vm_list(request):
    vms = VirtualMachine.objects.filter(owner=request.user)
    return render(request, 'frontend/vm_list.html', {'vms': vms})

@login_required
def vm_detail(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)
    return render(request, 'frontend/vm_detail.html', {'vm': vm})
