"""
虚拟机管理视图
"""
import logging
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from apps.vms.models import VirtualMachine
from apps.vms.serializers import (
    VirtualMachineSerializer, 
    VirtualMachineCreateSerializer,
    VirtualMachineStatusSerializer,
    VirtualMachineMetricsSerializer,
    VirtualMachineOperationSerializer,
    VNCAccessSerializer
)
from apps.vms.services import vm_service
from apps.vms.libvirt_manager import libvirt_manager
import os, shutil
from django.conf import settings
from apps.courses.models import VirtualMachineTemplate
from apps.courses.serializers import VirtualMachineTemplateSerializer

logger = logging.getLogger(__name__)


class VirtualMachineViewSet(viewsets.ModelViewSet):
    """
    虚拟机视图集
    """
    serializer_class = VirtualMachineSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        根据用户角色返回不同的虚拟机列表
        """
        user = self.request.user
        user_role = getattr(user, 'role', None)
        role_name = getattr(user_role, 'name', None) if user_role else None
        
        if user.is_staff or role_name == 'admin':
            # 管理员可以看到所有虚拟机
            return VirtualMachine.objects.all().order_by('-created_at')
        elif role_name == 'teacher':
            # 教师可以看到自己的虚拟机和自己课程中学生的虚拟机
            return VirtualMachine.objects.filter(
                Q(owner=user) | Q(course__teachers=user)
            ).distinct().order_by('-created_at')
        else:
            # 学生只能看到自己的虚拟机
            return VirtualMachine.objects.filter(owner=user).order_by('-created_at')
    
    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'create':
            return VirtualMachineCreateSerializer
        return VirtualMachineSerializer
    
    def create(self, request, *args, **kwargs):
        """
        创建虚拟机
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 保存虚拟机记录
        vm = serializer.save()
        
        # 异步创建虚拟机
        vm_service.create_vm_async(str(vm.id))
        
        return Response({
            'id': vm.id,
            'name': vm.name,
            'status': vm.status,
            'message': '虚拟机创建任务已启动'
        }, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """
        删除虚拟机
        """
        vm = self.get_object()
        
        # 检查权限
        if not self._check_vm_permission(vm, request.user):
            return Response(
                {'error': '您没有权限删除此虚拟机'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 删除虚拟机
        result = vm_service.delete_vm(str(vm.id), remove_disk=True)
        
        if result['success']:
            return Response({
                'message': '虚拟机删除成功'
            }, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({
                'error': result['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _check_vm_permission(self, vm, user):
        """检查用户是否有权限操作虚拟机"""
        user_role = getattr(user, 'role', None)
        role_name = getattr(user_role, 'name', None) if user_role else None
        
        if user.is_staff or role_name == 'admin':
            return True
        elif vm.owner == user:
            return True
        elif role_name == 'teacher' and vm.course and vm.course.teachers.filter(id=user.id).exists():
            return True
        return False
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """启动虚拟机"""
        vm = self.get_object()
        
        if not self._check_vm_permission(vm, request.user):
            return Response(
                {'error': '您没有权限操作此虚拟机'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if vm.status == 'running':
            return Response({'message': '虚拟机已经在运行'})
        
        # 启动虚拟机
        result = vm_service.start_vm(str(vm.id))
        
        if result['success']:
            # 启动 websockify
            vm.refresh_from_db() # 确保获取到最新的 vnc_port
            vm_service.start_websockify(vm)
            return Response({
                'message': '虚拟机启动成功'
            })
        else:
            return Response({
                'error': result['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """停止虚拟机"""
        vm = self.get_object()
        
        if not self._check_vm_permission(vm, request.user):
            return Response(
                {'error': '您没有权限操作此虚拟机'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = VirtualMachineOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        force = serializer.validated_data.get('force', False)
        
        if vm.status == 'stopped':
            return Response({'message': '虚拟机已经停止'})
        
        # 停止虚拟机
        result = vm_service.stop_vm(str(vm.id), force=force)
        
        if result['success']:
            return Response({
                'message': '虚拟机停止成功'
            })
        else:
            return Response({
                'error': result['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def restart(self, request, pk=None):
        """重启虚拟机"""
        vm = self.get_object()
        
        if not self._check_vm_permission(vm, request.user):
            return Response(
                {'error': '您没有权限操作此虚拟机'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if vm.status != 'running':
            return Response(
                {'error': '只能重启运行中的虚拟机'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 重启虚拟机
        result = vm_service.restart_vm(str(vm.id))
        
        if result['success']:
            return Response({
                'message': '虚拟机重启成功'
            })
        else:
            return Response({
                'error': result['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """暂停虚拟机"""
        vm = self.get_object()
        
        if not self._check_vm_permission(vm, request.user):
            return Response(
                {'error': '您没有权限操作此虚拟机'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if vm.status != 'running':
            return Response(
                {'error': '只能暂停运行中的虚拟机'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 暂停虚拟机
        result = vm_service.pause_vm(str(vm.id))
        
        if result['success']:
            return Response({
                'message': '虚拟机暂停成功'
            })
        else:
            return Response({
                'error': result['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """恢复虚拟机"""
        vm = self.get_object()
        
        if not self._check_vm_permission(vm, request.user):
            return Response(
                {'error': '您没有权限操作此虚拟机'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if vm.status != 'paused':
            return Response(
                {'error': '只能恢复暂停的虚拟机'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 恢复虚拟机
        result = vm_service.resume_vm(str(vm.id))
        
        if result['success']:
            return Response({
                'message': '虚拟机恢复成功'
            })
        else:
            return Response({
                'error': result['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """获取虚拟机状态"""
        vm = self.get_object()
        
        if not self._check_vm_permission(vm, request.user):
            return Response(
                {'error': '您没有权限查看此虚拟机'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # 从libvirt获取实时状态
            vm_status = libvirt_manager.get_vm_status(vm.name)
            if vm_status:
                # 更新数据库中的状态
                vm.status = vm_status['state']
                vm.ip_address = vm_status['ip_address']
                vm.save()
                
                serializer = VirtualMachineStatusSerializer(vm_status)
                return Response(serializer.data)
            else:
                return Response(
                    {'error': '无法获取虚拟机状态'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"获取虚拟机状态失败: {e}")
            return Response(
                {'error': '获取虚拟机状态失败'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        """获取虚拟机监控指标"""
        vm = self.get_object()
        
        if not self._check_vm_permission(vm, request.user):
            return Response(
                {'error': '您没有权限查看此虚拟机'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # 从libvirt获取监控指标
            metrics = libvirt_manager.get_vm_metrics(vm.name)
            if metrics:
                serializer = VirtualMachineMetricsSerializer(metrics)
                return Response(serializer.data)
            else:
                return Response(
                    {'error': '无法获取虚拟机监控指标'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"获取虚拟机监控指标失败: {e}")
            return Response(
                {'error': '获取虚拟机监控指标失败'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def console_vnc(self, request, pk=None):
        """获取VNC控制台访问信息"""
        vm = self.get_object()
        
        if not self._check_vm_permission(vm, request.user):
            return Response(
                {'error': '您没有权限访问此虚拟机控制台'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if vm.status != 'running':
            return Response(
                {'error': '虚拟机必须处于运行状态才能访问控制台'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 确保 websockify 正在运行
        websockify_port = vm_service.start_websockify(vm)
        if not websockify_port:
            return Response(
                {'error': '无法启动 VNC 代理服务'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            # 获取VNC访问信息
            vnc_data = {
                'websockify_port': websockify_port,
                'vnc_password': vm.vnc_password
            }
            
            serializer = VNCAccessSerializer(data=vnc_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        except VirtualMachine.DoesNotExist:
            return Response({'error': '虚拟机未找到'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"获取VNC访问信息失败: {e}")
            return Response(
                {'error': '获取VNC访问信息失败'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def my_vms(self, request):
        """获取当前用户的虚拟机列表"""
        user_vms = VirtualMachine.objects.filter(owner=request.user).order_by('-created_at')
        serializer = self.get_serializer(user_vms, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def course_vms(self, request):
        """获取指定课程的虚拟机列表"""
        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response(
                {'error': '请指定课程ID'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查用户是否有权限查看此课程的虚拟机
        user_role = getattr(request.user, 'role', None)
        role_name = getattr(user_role, 'name', None) if user_role else None
        
        if request.user.is_staff or role_name == 'admin':
            # 管理员可以查看所有课程的虚拟机
            vms = VirtualMachine.objects.filter(course_id=course_id)
        elif role_name == 'teacher':
            # 教师只能查看自己教授课程的虚拟机
            vms = VirtualMachine.objects.filter(
                course_id=course_id,
                course__teachers=request.user
            )
        else:
            # 学生只能查看自己在此课程中的虚拟机
            vms = VirtualMachine.objects.filter(
                course_id=course_id,
                owner=request.user
            )
        
        serializer = self.get_serializer(vms.order_by('-created_at'), many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def convert_to_template(self, request, pk=None):
        """将虚拟机转换为模板，仅限课程教师"""
        vm = self.get_object()
        # 权限校验：仅课程教师或管理员
        user = request.user
        user_role = getattr(user, 'role', None)
        role_name = getattr(user_role, 'name', None) if user_role else None
        is_teacher = (role_name == 'teacher' and vm.course and vm.course.teachers.filter(id=user.id).exists())
        if not (user.is_staff or role_name == 'admin' or is_teacher):
            return Response({'error': '您没有权限转换此虚拟机'}, status=status.HTTP_403_FORBIDDEN)
        # 获取模板名称与描述
        name = request.data.get('name', vm.name)
        description = request.data.get('description', '')
        # 复制磁盘文件
        src = os.path.join(settings.LIBVIRT_STORAGE_DIR, f"{vm.name}.qcow2")
        dest_dir = os.path.join(settings.LIBVIRT_STORAGE_DIR, 'templates')
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, f"{name}_{vm.name}.qcow2")
        try:
            shutil.copyfile(src, dest)
            template = VirtualMachineTemplate.objects.create(
                name=name,
                description=description,
                file_path=dest,
                owner=request.user,
                course=vm.course
            )
            serializer = VirtualMachineTemplateSerializer(template)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"VM转换为模板失败: {e}")
            return Response({'error': '转换失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
