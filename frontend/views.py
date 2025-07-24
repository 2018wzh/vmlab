from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, CourseForm, VMForm
from django.contrib.auth.decorators import login_required
from apps.courses.models import Course
from apps.vms.models import VirtualMachine
from django.contrib.auth import get_user_model
from .forms import UserForm


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
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('frontend:course_list')
    else:
        form = CourseForm()
    return render(request, 'frontend/course_form.html', {'form': form, 'title': '创建课程'})

@login_required
def course_update(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('frontend:course_detail', course_id=course.pk)
    else:
        form = CourseForm(instance=course)
    return render(request, 'frontend/course_form.html', {'form': form, 'title': '编辑课程'})

@login_required
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.delete()
        return redirect('frontend:course_list')
    return render(request, 'frontend/course_confirm_delete.html', {'course': course})

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
def vm_list_partial(request):
    """HTMX 局部刷新虚拟机列表行"""
    vms = VirtualMachine.objects.filter(owner=request.user)
    return render(request, 'frontend/partials/vm_list_rows.html', {'vms': vms})

@login_required
def vm_create(request):
    if request.method == 'POST':
        form = VMForm(request.POST)
        if form.is_valid():
            vm = form.save(commit=False)
            vm.owner = request.user
            vm.save()
            return redirect('frontend:vm_list')
    else:
        form = VMForm()
    return render(request, 'frontend/vm_form.html', {'form': form, 'title': '创建虚拟机'})

@login_required
def vm_update(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)
    if request.method == 'POST':
        form = VMForm(request.POST, instance=vm, initial={'owner': request.user})
        if form.is_valid():
            form.save()
            return redirect('frontend:vm_detail', vm_id=vm.pk)
    else:
        form = VMForm(instance=vm)
    return render(request, 'frontend/vm_form.html', {'form': form, 'title': '编辑虚拟机'})

@login_required
def vm_delete(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)
    if request.method == 'POST':
        vm.delete()
        return redirect('frontend:vm_list')
    return render(request, 'frontend/vm_confirm_delete.html', {'vm': vm})
   
# 用户管理视图
User = get_user_model()

@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'frontend/user_list.html', {'users': users})

@login_required
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('frontend:user_list')
    else:
        form = UserForm()
    return render(request, 'frontend/user_form.html', {'form': form, 'title': '创建用户'})

@login_required
def user_update(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('frontend:user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'frontend/user_form.html', {'form': form, 'title': '编辑用户'})

@login_required
def user_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    return redirect('frontend:user_list')

@login_required
def vm_detail(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)
    return render(request, 'frontend/vm_detail.html', {'vm': vm})
