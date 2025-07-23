from django.db import models
from django.conf import settings
import uuid

from apps.courses.models import Course, VirtualMachineTemplate

class VirtualMachine(models.Model):
    """
    虚拟机模型
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="虚拟机名称")
    uuid = models.CharField(max_length=255, unique=True, blank=True, null=True, verbose_name="Libvirt中的UUID")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="虚拟机所有者")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所属课程")
    template = models.ForeignKey(VirtualMachineTemplate, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="创建时使用的模板")
    cpu_cores = models.IntegerField(verbose_name="CPU核心数")
    memory_mb = models.IntegerField(verbose_name="内存大小 (MB)")
    disk_gb = models.IntegerField(verbose_name="磁盘大小 (GB)")
    status = models.CharField(max_length=50, default="stopped", verbose_name="虚拟机状态")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP地址")
    mac_address = models.CharField(max_length=17, blank=True, null=True, verbose_name="MAC地址")
    vnc_port = models.IntegerField(blank=True, null=True, verbose_name="VNC端口")
    vnc_password = models.CharField(max_length=255, blank=True, null=True, verbose_name="VNC密码")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "虚拟机"
        verbose_name_plural = verbose_name
