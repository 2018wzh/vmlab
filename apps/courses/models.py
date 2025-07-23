from django.db import models
from django.conf import settings

class Course(models.Model):
    """
    课程模型
    """
    name = models.CharField(max_length=255, verbose_name="课程名称")
    description = models.TextField(blank=True, null=True, verbose_name="课程描述")
    teachers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="teaching_courses", verbose_name="授课教师")
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="enrolled_courses", blank=True, verbose_name="选课学生")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "课程"
        verbose_name_plural = verbose_name

class VirtualMachineTemplate(models.Model):
    """
    虚拟机模板模型
    """
    name = models.CharField(max_length=255, verbose_name="模板名称")
    description = models.TextField(blank=True, null=True, verbose_name="模板描述")
    file_path = models.CharField(max_length=1024, verbose_name="qcow2文件路径")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="上传者")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="vm_templates", verbose_name="模板所属课程")
    is_public = models.BooleanField(default=False, verbose_name="是否公开")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "虚拟机模板"
        verbose_name_plural = verbose_name
