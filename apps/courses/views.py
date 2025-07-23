from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Course, VirtualMachineTemplate
from .serializers import (
    CourseSerializer, CourseCreateSerializer, CourseDetailSerializer,
    VirtualMachineTemplateSerializer, UserBasicSerializer
)

User = get_user_model()

def index(request):
    return HttpResponse("Courses index")

class IsTeacherOrAdmin(permissions.BasePermission):
    """
    只允许教师或管理员进行某些操作
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        if not request.user.is_authenticated:
            return False
            
        user_role = getattr(request.user, 'role', None)
        role_name = getattr(user_role, 'name', None) if user_role else None
        
        return (request.user.is_staff or role_name in ['teacher', 'admin'])

class CourseViewSet(viewsets.ModelViewSet):
    """
    课程视图集
    """
    queryset = Course.objects.all().order_by('-created_at')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CourseCreateSerializer
        elif self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer

    def get_permissions(self):
        """
        根据操作类型设置不同的权限
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsTeacherOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        根据用户角色返回不同的课程列表
        """
        user = self.request.user
        user_role = getattr(user, 'role', None)
        role_name = getattr(user_role, 'name', None) if user_role else None
        
        if user.is_staff or role_name == 'admin':
            # 管理员可以看到所有课程
            return Course.objects.all().order_by('-created_at')
        elif role_name == 'teacher':
            # 教师只能看到自己教授的课程
            return Course.objects.filter(teachers=user).order_by('-created_at')
        else:
            # 学生只能看到自己选修的课程
            return Course.objects.filter(students=user).order_by('-created_at')

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """
        获取课程学生列表
        """
        course = self.get_object()
        students = course.students.all()
        serializer = UserBasicSerializer(students, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_student(self, request, pk=None):
        """
        添加学生到课程
        """
        course = self.get_object()
        student_id = request.data.get('student_id')
        
        try:
            student = User.objects.get(id=student_id, role__name='student')
            course.students.add(student)
            return Response({'message': '学生添加成功'})
        except User.DoesNotExist:
            return Response({'error': '学生不存在'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['delete'], url_path='students/(?P<user_id>[^/.]+)')
    def remove_student(self, request, pk=None, user_id=None):
        """
        从课程移除学生
        """
        course = self.get_object()
        try:
            student = User.objects.get(id=user_id)
            course.students.remove(student)
            return Response({'message': '学生移除成功'})
        except User.DoesNotExist:
            return Response({'error': '学生不存在'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def teachers(self, request, pk=None):
        """
        获取课程教师列表
        """
        course = self.get_object()
        teachers = course.teachers.all()
        serializer = UserBasicSerializer(teachers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_teacher(self, request, pk=None):
        """
        添加教师到课程
        """
        course = self.get_object()
        teacher_id = request.data.get('teacher_id')
        
        try:
            teacher = User.objects.get(id=teacher_id, role__name='teacher')
            course.teachers.add(teacher)
            return Response({'message': '教师添加成功'})
        except User.DoesNotExist:
            return Response({'error': '教师不存在'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['delete'], url_path='teachers/(?P<user_id>[^/.]+)')
    def remove_teacher(self, request, pk=None, user_id=None):
        """
        从课程移除教师
        """
        course = self.get_object()
        try:
            teacher = User.objects.get(id=user_id)
            course.teachers.remove(teacher)
            return Response({'message': '教师移除成功'})
        except User.DoesNotExist:
            return Response({'error': '教师不存在'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def templates(self, request, pk=None):
        """
        获取课程虚拟机模板列表
        """
        course = self.get_object()
        templates = course.vm_templates.all()
        serializer = VirtualMachineTemplateSerializer(templates, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_template(self, request, pk=None):
        """
        为课程添加虚拟机模板
        """
        course = self.get_object()
        serializer = VirtualMachineTemplateSerializer(
            data=request.data, 
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(course=course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        获取课程统计信息
        """
        course = self.get_object()
        
        # 获取虚拟机模型
        from apps.vms.models import VirtualMachine
        
        # 统计数据
        stats = {
            'total_students': course.students.count(),
            'total_teachers': course.teachers.count(),
            'total_templates': course.vm_templates.count(),
            'total_vms': VirtualMachine.objects.filter(course=course).count(),
            'running_vms': VirtualMachine.objects.filter(course=course, status='running').count(),
            'stopped_vms': VirtualMachine.objects.filter(course=course, status='stopped').count(),
        }
        
        return Response(stats)

class VirtualMachineTemplateViewSet(viewsets.ModelViewSet):
    """
    虚拟机模板视图集
    """
    queryset = VirtualMachineTemplate.objects.all().order_by('-created_at')
    serializer_class = VirtualMachineTemplateSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        """
        根据用户角色返回不同的模板列表
        """
        user = self.request.user
        user_role = getattr(user, 'role', None)
        role_name = getattr(user_role, 'name', None) if user_role else None
        
        if user.is_staff or role_name == 'admin':
            # 管理员可以看到所有模板
            return VirtualMachineTemplate.objects.all().order_by('-created_at')
        elif role_name == 'teacher':
            # 教师只能看到自己创建的模板和公开模板
            return VirtualMachineTemplate.objects.filter(
                Q(owner=user) | Q(is_public=True)
            ).order_by('-created_at')
        else:
            # 学生只能看到公开模板和自己课程的模板
            user_courses = Course.objects.filter(students=user)
            return VirtualMachineTemplate.objects.filter(
                Q(is_public=True) | Q(course__in=user_courses)
            ).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """
        验证模板文件
        """
        template = self.get_object()
        # 这里可以添加文件验证逻辑
        # 例如检查文件是否存在、是否为有效的qcow2格式等
        import os
        
        if os.path.exists(template.file_path):
            # 简单检查文件扩展名
            if template.file_path.endswith('.qcow2'):
                return Response({'valid': True, 'message': '模板文件验证通过'})
            else:
                return Response({'valid': False, 'message': '文件格式不正确，需要qcow2格式'})
        else:
            return Response({'valid': False, 'message': '模板文件不存在'}, 
                          status=status.HTTP_404_NOT_FOUND)
