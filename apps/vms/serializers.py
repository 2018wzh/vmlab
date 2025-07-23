"""
虚拟机序列化器
"""
from rest_framework import serializers
from django.db import models
from apps.vms.models import VirtualMachine
from apps.courses.models import Course, VirtualMachineTemplate
from apps.users.models import Quota


class VirtualMachineSerializer(serializers.ModelSerializer):
    """
    虚拟机序列化器
    """
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = VirtualMachine
        fields = [
            'id', 'name', 'uuid', 'owner', 'owner_username',
            'course', 'course_name', 'template', 'template_name',
            'cpu_cores', 'memory_mb', 'disk_gb', 'status',
            'ip_address', 'mac_address', 'vnc_port', 'vnc_password',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'status', 'ip_address', 'mac_address', 
                           'vnc_port', 'vnc_password', 'created_at', 'updated_at']


class VirtualMachineCreateSerializer(serializers.ModelSerializer):
    """
    虚拟机创建序列化器
    """
    template_id = serializers.UUIDField(source='template.id', write_only=True)
    course_id = serializers.UUIDField(source='course.id', write_only=True, required=False)
    
    class Meta:
        model = VirtualMachine
        fields = [
            'name', 'template_id', 'course_id', 'cpu_cores', 'memory_mb', 'disk_gb'
        ]
    
    def validate(self, attrs):
        """验证虚拟机创建参数"""
        user = self.context['request'].user
        template_id = attrs.get('template', {}).get('id')
        course_id = attrs.get('course', {}).get('id')
        
        # 验证模板存在且有权限访问
        try:
            template = VirtualMachineTemplate.objects.get(id=template_id)
            attrs['template'] = template
        except VirtualMachineTemplate.DoesNotExist:
            raise serializers.ValidationError("指定的模板不存在")
        
        # 验证课程权限
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                # 检查用户是否有权限在这个课程中创建虚拟机
                if not (course.students.filter(id=user.id).exists() or 
                       course.teachers.filter(id=user.id).exists() or
                       user.is_staff):
                    raise serializers.ValidationError("您没有在此课程中创建虚拟机的权限")
                attrs['course'] = course
            except Course.DoesNotExist:
                raise serializers.ValidationError("指定的课程不存在")
        
        # 验证资源配额
        try:
            quota = Quota.objects.get(user=user)
            
            # 检查CPU配额
            used_cpu = VirtualMachine.objects.filter(owner=user).aggregate(
                total=models.Sum('cpu_cores'))['total'] or 0
            if used_cpu + attrs['cpu_cores'] > quota.cpu_cores:
                raise serializers.ValidationError(f"CPU配额不足，当前已使用{used_cpu}核，配额{quota.cpu_cores}核")
            
            # 检查内存配额
            used_memory = VirtualMachine.objects.filter(owner=user).aggregate(
                total=models.Sum('memory_mb'))['total'] or 0
            if used_memory + attrs['memory_mb'] > quota.memory_mb:
                raise serializers.ValidationError(f"内存配额不足，当前已使用{used_memory}MB，配额{quota.memory_mb}MB")
            
            # 检查磁盘配额
            used_disk = VirtualMachine.objects.filter(owner=user).aggregate(
                total=models.Sum('disk_gb'))['total'] or 0
            if used_disk + attrs['disk_gb'] > quota.disk_gb:
                raise serializers.ValidationError(f"磁盘配额不足，当前已使用{used_disk}GB，配额{quota.disk_gb}GB")
            
            # 检查虚拟机数量限制
            vm_count = VirtualMachine.objects.filter(owner=user).count()
            if vm_count >= quota.vm_limit:
                raise serializers.ValidationError(f"虚拟机数量已达上限，当前{vm_count}台，上限{quota.vm_limit}台")
                
        except Quota.DoesNotExist:
            raise serializers.ValidationError("用户配额信息不存在，请联系管理员")
        
        return attrs
    
    def create(self, validated_data):
        """创建虚拟机"""
        user = self.context['request'].user
        validated_data['owner'] = user
        return super().create(validated_data)


class VirtualMachineStatusSerializer(serializers.Serializer):
    """
    虚拟机状态序列化器
    """
    name = serializers.CharField()
    state = serializers.CharField()
    vnc_port = serializers.CharField(allow_null=True)
    ip_address = serializers.CharField(allow_null=True)
    is_active = serializers.BooleanField()


class VirtualMachineMetricsSerializer(serializers.Serializer):
    """
    虚拟机监控指标序列化器
    """
    cpu_usage = serializers.IntegerField()
    memory_usage = serializers.IntegerField()
    memory_available = serializers.IntegerField()
    disk_read = serializers.IntegerField()
    disk_write = serializers.IntegerField()
    network_rx = serializers.IntegerField()
    network_tx = serializers.IntegerField()


class VirtualMachineOperationSerializer(serializers.Serializer):
    """
    虚拟机操作序列化器
    """
    force = serializers.BooleanField(default=False, required=False)
    
    
class VNCAccessSerializer(serializers.Serializer):
    """
    VNC访问序列化器
    """
    vnc_url = serializers.CharField()
    vnc_port = serializers.IntegerField()
    vnc_password = serializers.CharField(allow_null=True)
