from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
import os, shutil
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, CourseForm, VMForm, VMConvertForm
from django.contrib.auth.decorators import login_required
from apps.courses.models import Course, VirtualMachineTemplate
from apps.vms.models import VirtualMachine
from django.contrib.auth import get_user_model
from .forms import UserForm, CourseStudentForm, VMTemplateForm
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from apps.vms.services import vm_service


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
    """根据用户角色渲染不同的 Dashboard 页面"""
    user = request.user
    role_name = getattr(getattr(user, 'role', None), 'name', None)
    # 教师
    if role_name == 'teacher':
        courses = Course.objects.filter(teachers=user)
        vms = VirtualMachine.objects.filter(
            Q(owner=user) | Q(course__teachers=user)
        ).distinct().order_by('-created_at')
        template_name = 'frontend/dashboard_teacher.html'
    # 管理员
    elif user.is_staff or role_name == 'admin':
        courses = Course.objects.all()
        vms = VirtualMachine.objects.all().order_by('-created_at')
        template_name = 'frontend/dashboard_admin.html'
    # 学生及其他
    else:
        courses = Course.objects.filter(students=user)
        vms = VirtualMachine.objects.filter(owner=user).order_by('-created_at')
        template_name = 'frontend/dashboard_student.html'
    return render(request, template_name, {'courses': courses, 'vms': vms})

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
    course.delete()
    return redirect('frontend:course_list')

@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'frontend/course_list.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = course.students.all()
    teachers = course.teachers.all()
    # 课程添加学生表单
    add_student_form = CourseStudentForm()
    return render(request, 'frontend/course_detail.html', {
        'course': course,
        'students': students,
        'teachers': teachers,
        'add_student_form': add_student_form,
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
            # 异步创建虚拟机
            vm_service.create_vm_async(str(vm.id))
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
    vm.delete()
    return redirect('frontend:vm_list')
   
@login_required
def vm_detail(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)
    return render(request, 'frontend/vm_detail.html', {'vm': vm})
   
@login_required
def vm_convert(request, vm_id):
    vm = get_object_or_404(VirtualMachine, id=vm_id)
    # 仅课程教师可转换
    if not vm.course or (not request.user.is_staff and request.user not in vm.course.teachers.all()):
        return redirect('frontend:vm_detail', vm_id=vm_id)
    if request.method == 'POST':
        form = VMConvertForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            # 复制虚拟机磁盘为模板文件
            src = os.path.join(settings.LIBVIRT_STORAGE_DIR, f"{vm.name}.qcow2")
            dest_dir = os.path.join(settings.LIBVIRT_STORAGE_DIR, 'templates')
            os.makedirs(dest_dir, exist_ok=True)
            dest = os.path.join(dest_dir, f"{template.name}_{vm.name}.qcow2")
            shutil.copyfile(src, dest)
            template.file_path = dest
            template.owner = request.user
            template.save()
            return redirect('frontend:template_detail', template_id=template.id)
    else:
        initial = {'name': vm.name, 'course': vm.course.pk if vm.course else None}
        form = VMConvertForm(initial=initial)
    return render(request, 'frontend/vm_convert.html', {'form': form, 'vm': vm})

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
def course_add_student(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    form = CourseStudentForm(request.POST)
    if form.is_valid():
        student = form.cleaned_data['student']
        course.students.add(student)
    return redirect('frontend:course_detail', course_id=course_id)

@login_required
def course_remove_student(request, course_id, user_id):
    course = get_object_or_404(Course, id=course_id)
    User = get_user_model()
    student = get_object_or_404(User, pk=user_id)
    course.students.remove(student)
    return redirect('frontend:course_detail', course_id=course_id)

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
def user_profile(request):
    """展示当前用户个人信息"""
    return render(request, 'frontend/user_profile.html', {'user': request.user})

@login_required
def template_list(request):
    """虚拟机模板列表"""
    # 显示用户拥有或公开的模板
    templates = VirtualMachineTemplate.objects.filter(
        Q(owner=request.user) | Q(is_public=True)
    )
    return render(request, 'frontend/template_list.html', {'templates': templates})

@login_required
def template_create(request):
    """创建虚拟机模板"""
    if request.method == 'POST':
        form = VMTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.save(commit=False)
            template.owner = request.user
            # 保存上传文件
            file = request.FILES.get('file')
            fs = FileSystemStorage(location=str(settings.MEDIA_ROOT) + '/templates')
            filename = fs.save(file.name, file)
            template.file_path = fs.path(filename)
            template.save()
            return redirect('frontend:template_list')
    else:
        form = VMTemplateForm()
    return render(request, 'frontend/template_form.html', {'form': form, 'title': '创建模板'})

@login_required
def template_detail(request, template_id):
    """虚拟机模板详情"""
    template = get_object_or_404(VirtualMachineTemplate, id=template_id)
    return render(request, 'frontend/template_detail.html', {'template': template})

@login_required
def template_delete(request, template_id):
    """删除虚拟机模板"""
    template = get_object_or_404(VirtualMachineTemplate, id=template_id)
    # 删除文件
    try:
        os.remove(template.file_path)
    except Exception:
        pass
    template.delete()
    return redirect('frontend:template_list')

