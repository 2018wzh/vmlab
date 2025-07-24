import pytest
from django.contrib.auth import get_user_model
from apps.users.models import Quota
from apps.courses.models import Course, VirtualMachineTemplate
from apps.vms.models import VirtualMachine
from frontend.forms import CourseForm, VMForm

pytestmark = pytest.mark.django_db

User = get_user_model()

@pytest.fixture
def sample_users():
    teacher = User.objects.create_user(username='teacher1', password='pass12345')
    student = User.objects.create_user(username='student1', password='pass12345')
    return teacher, student

@pytest.fixture
def sample_course(sample_users):
    teacher, student = sample_users
    course = Course.objects.create(name='CourseA', description='DescA')
    course.teachers.add(teacher)
    course.students.add(student)
    return course

@pytest.fixture
def sample_template(sample_course, sample_users):
    teacher, _ = sample_users
    template = VirtualMachineTemplate.objects.create(
        name='Tpl1', description='TplDesc', file_path='/tmp/tpl.qcow2', owner=teacher, course=sample_course
    )
    return template


def test_course_form_valid_and_save(sample_users):
    teacher, student = sample_users
    data = {
        'name': 'TestCourse',
        'description': 'TestDesc',
        'teachers': [teacher.pk],
        'students': [student.pk],
    }
    form = CourseForm(data)
    assert form.is_valid()
    course = form.save()
    assert Course.objects.filter(name='TestCourse').exists()
    assert list(course.teachers.all()) == [teacher]
    assert list(course.students.all()) == [student]


def test_course_form_invalid_missing_name():
    data = {'name': '', 'description': 'X', 'teachers': [], 'students': []}
    form = CourseForm(data)
    assert not form.is_valid()
    assert 'name' in form.errors


def test_vm_form_quota_validation(sample_users, sample_course, sample_template):
    teacher, student = sample_users
    # 创建配额
    Quota.objects.create(user=student, cpu_cores=2, memory_mb=1024, disk_gb=50, vm_limit=5)
    valid_data = {
        'name': 'VM1',
        'course': sample_course.pk,
        'template': sample_template.pk,
        'cpu_cores': 1,
        'memory_mb': 512,
        'disk_gb': 20,
    }
    # 有效数据
    form = VMForm(valid_data, initial={'owner': student})
    assert form.is_valid()
    vm = form.save(commit=False)
    vm.owner = student
    vm.save()
    assert VirtualMachine.objects.filter(name='VM1').exists()
    # 超出 CPU 配额
    data2 = valid_data.copy()
    data2['cpu_cores'] = 3
    form2 = VMForm(data2, initial={'owner': student})
    assert not form2.is_valid()
    assert 'cpu_cores' in form2.errors
    # 超出 内存 配额
    data3 = valid_data.copy()
    data3['memory_mb'] = 2048
    form3 = VMForm(data3, initial={'owner': student})
    assert not form3.is_valid()
    assert 'memory_mb' in form3.errors
    # 超出 磁盘 配额
    data4 = valid_data.copy()
    data4['disk_gb'] = 100
    form4 = VMForm(data4, initial={'owner': student})
    assert not form4.is_valid()
    assert 'disk_gb' in form4.errors
