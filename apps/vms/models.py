from django.db import models
from django.conf import settings
import uuid

from apps.courses.models import Course, VirtualMachineTemplate

class VirtualMachine(models.Model):
    """
    虚拟机模型
    """
    STATUS_CHOICES = [
        ('creating', '创建中'),
        ('stopped', '已停止'),
        ('running', '运行中'),
        ('paused', '已暂停'),
        ('error', '错误'),
        ('deleting', '删除中'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="虚拟机名称")
    uuid = models.CharField(max_length=255, unique=True, blank=True, null=True, verbose_name="Libvirt中的UUID")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="虚拟机所有者")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所属课程")
    template = models.ForeignKey(VirtualMachineTemplate, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="创建时使用的模板")
    cpu_cores = models.IntegerField(verbose_name="CPU核心数")
    memory_mb = models.IntegerField(verbose_name="内存大小 (MB)")
    disk_gb = models.IntegerField(verbose_name="磁盘大小 (GB)")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="stopped", verbose_name="虚拟机状态")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP地址")
    mac_address = models.CharField(max_length=17, blank=True, null=True, verbose_name="MAC地址")
    vnc_port = models.IntegerField(blank=True, null=True, verbose_name="VNC端口")
    vnc_password = models.CharField(max_length=255, blank=True, null=True, verbose_name="VNC密码")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name
    
    @property
    def is_running(self):
        """是否在运行"""
        return self.status == 'running'
    
    @property
    def is_stopped(self):
        """是否已停止"""
        return self.status == 'stopped'
    
    @property
    def is_paused(self):
        """是否已暂停"""
        return self.status == 'paused'
    
    @property
    def can_start(self):
        """是否可以启动"""
        return self.status in ['stopped', 'error']
    
    @property
    def can_stop(self):
        """是否可以停止"""
        return self.status in ['running', 'paused']
    
    @property
    def can_pause(self):
        """是否可以暂停"""
        return self.status == 'running'
    
    @property
    def can_resume(self):
        """是否可以恢复"""
        return self.status == 'paused'
    
    def get_status_display_color(self):
        """获取状态显示颜色"""
        color_map = {
            'creating': 'blue',
            'stopped': 'gray',
            'running': 'green',
            'paused': 'yellow',
            'error': 'red',
            'deleting': 'orange',
        }
        return color_map.get(self.status, 'gray')

    class Meta:
        verbose_name = "虚拟机"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
