from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, VirtualMachineTemplate

User = get_user_model()

class CourseSerializer(serializers.ModelSerializer):
    """
    课程序列化器
    """
    teachers = serializers.StringRelatedField(many=True, read_only=True)
    students = serializers.StringRelatedField(many=True, read_only=True)
    teachers_count = serializers.SerializerMethodField()
    students_count = serializers.SerializerMethodField()
    vm_templates_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'name', 'description', 'teachers', 'students',
            'teachers_count', 'students_count', 'vm_templates_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_teachers_count(self, obj):
        return obj.teachers.count()

    def get_students_count(self, obj):
        return obj.students.count()

    def get_vm_templates_count(self, obj):
        return obj.vm_templates.count()

class CourseCreateSerializer(serializers.ModelSerializer):
    """
    课程创建序列化器
    """
    teacher_ids = serializers.ListField(
        child=serializers.UUIDField(), 
        write_only=True,
        required=False,
        help_text="教师ID列表"
    )
    student_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="学生ID列表"
    )

    class Meta:
        model = Course
        fields = ['name', 'description', 'teacher_ids', 'student_ids']

    def create(self, validated_data):
        teacher_ids = validated_data.pop('teacher_ids', [])
        student_ids = validated_data.pop('student_ids', [])
        
        course = Course.objects.create(**validated_data)
        
        # 添加教师
        if teacher_ids:
            teachers = User.objects.filter(id__in=teacher_ids, role__name='teacher')
            course.teachers.set(teachers)
        
        # 添加学生
        if student_ids:
            students = User.objects.filter(id__in=student_ids, role__name='student')
            course.students.set(students)
        
        return course

class VirtualMachineTemplateSerializer(serializers.ModelSerializer):
    """
    虚拟机模板序列化器
    """
    owner = serializers.StringRelatedField(read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = VirtualMachineTemplate
        fields = [
            'id', 'name', 'description', 'file_path', 'owner',
            'course', 'course_name', 'is_public', 'created_at'
        ]
        read_only_fields = ['created_at', 'owner']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class UserBasicSerializer(serializers.ModelSerializer):
    """
    用户基本信息序列化器（用于课程成员管理）
    """
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role_name']

class CourseDetailSerializer(serializers.ModelSerializer):
    """
    课程详情序列化器
    """
    teachers = UserBasicSerializer(many=True, read_only=True)
    students = UserBasicSerializer(many=True, read_only=True)
    vm_templates = VirtualMachineTemplateSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'name', 'description', 'teachers', 'students',
            'vm_templates', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
