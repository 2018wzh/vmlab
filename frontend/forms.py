from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from apps.courses.models import Course
from apps.vms.models import VirtualMachine
from apps.users.models import Quota
from apps.courses.models import VirtualMachineTemplate

class CustomUserCreationForm(UserCreationForm):
    """Use custom user model for registration."""
    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2')
 
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description', 'teachers', 'students']
        widgets = {
            'teachers': forms.CheckboxSelectMultiple,
            'students': forms.CheckboxSelectMultiple,
        }

class VMForm(forms.ModelForm):
    class Meta:
        model = VirtualMachine
        fields = ['name', 'course', 'template', 'cpu_cores', 'memory_mb', 'disk_gb']

    def clean(self):
        cleaned = super().clean()
        # 获取表单提交用户：优先使用 initial 中传入的 owner
        user = self.initial.get('owner')
        # 如果是已有实例且 initial 中无 owner，则使用实例 owner
        if not user and self.instance.pk:
            try:
                user = self.instance.owner
            except Exception:
                user = None
        # 获取用户配额
        if user:
            try:
                quota = Quota.objects.get(user=user)
            except Quota.DoesNotExist:
                return cleaned
        else:
            return cleaned
        # 校验资源
        cpu = cleaned.get('cpu_cores')
        mem = cleaned.get('memory_mb')
        disk = cleaned.get('disk_gb')
        if cpu and cpu > quota.cpu_cores:
            self.add_error('cpu_cores', '超出CPU配额')
        if mem and mem > quota.memory_mb:
            self.add_error('memory_mb', '超出内存配额')
        if disk and disk > quota.disk_gb:
            self.add_error('disk_gb', '超出磁盘配额')
        # TODO: VM 数量限制校验
        return cleaned
 
# 用户管理表单
User = get_user_model()
class UserForm(forms.ModelForm):
    # 密码字段
    password1 = forms.CharField(label='密码', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='确认密码', widget=forms.PasswordInput, required=False)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'is_active', 'is_staff']
        widgets = {
            'role': forms.Select,
        }
    
# 课程成员管理表单
class CourseStudentForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(role__name='student'),
        label='选择学生',
        widget=forms.Select
    )

# 虚拟机模板管理表单
class VMTemplateForm(forms.ModelForm):
    file = forms.FileField(label='QCOW2 文件')
    class Meta:
        model = VirtualMachineTemplate
        fields = ['name', 'description', 'course', 'is_public']
        widgets = {
            'course': forms.Select,
        }

