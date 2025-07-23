from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from .models import User, Role, Quota

class RoleSerializer(serializers.ModelSerializer):
    """
    角色序列化器
    """
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']

class QuotaSerializer(serializers.ModelSerializer):
    """
    配额序列化器
    """
    class Meta:
        model = Quota
        fields = ['cpu_cores', 'memory_mb', 'disk_gb', 'vm_limit']

class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器 (用于读取和更新)
    """
    role = serializers.StringRelatedField()
    quota = QuotaSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'quota', 'is_active', 'date_joined'
        ]
        read_only_fields = ['date_joined', 'id']

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次输入的密码不匹配。"})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        
        # 默认分配 "student" 角色
        try:
            student_role = Role.objects.get(name='student')
            user.role = student_role
        except Role.DoesNotExist:
            # 如果角色不存在，可以创建一个或设置为None
            pass
            
        user.save()
        
        # 创建默认配额
        Quota.objects.create(user=user)
        
        return user
