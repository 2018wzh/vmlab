from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class Role(models.Model):
    """
    角色模型
    """
    name = models.CharField(max_length=50, unique=True, verbose_name="角色名称")
    description = models.TextField(blank=True, null=True, verbose_name="角色描述")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = verbose_name

class User(AbstractUser):
    """
    用户模型
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="用户ID")
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="角色")
    
    class Meta(AbstractUser.Meta):
        verbose_name = "用户"
        verbose_name_plural = verbose_name

class Quota(models.Model):
    """
    资源配额模型
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    cpu_cores = models.IntegerField(default=4, verbose_name="CPU核心数配额")
    memory_mb = models.IntegerField(default=4096, verbose_name="内存配额 (MB)")
    disk_gb = models.IntegerField(default=100, verbose_name="磁盘空间配额 (GB)")
    vm_limit = models.IntegerField(default=5, verbose_name="虚拟机数量限制")

    def __str__(self):
        return f"{self.user.username} 的配额"

    class Meta:
        verbose_name = "资源配额"
        verbose_name_plural = verbose_name
