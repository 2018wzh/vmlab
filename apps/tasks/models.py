from django.db import models
from django.conf import settings

class Task(models.Model):
    """
    任务模型
    """
    id = models.AutoField(primary_key=True)
    task_id = models.CharField(max_length=255, unique=True, verbose_name="Celery任务ID")
    name = models.CharField(max_length=255, verbose_name="任务名称")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="任务发起者")
    status = models.CharField(max_length=50, default="PENDING", verbose_name="任务状态")
    result = models.JSONField(blank=True, null=True, verbose_name="任务结果")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name="完成时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "任务"
        verbose_name_plural = verbose_name
