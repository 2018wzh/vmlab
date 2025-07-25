"""
虚拟机管理服务（不使用Celery）
"""
import logging
import uuid
import threading
import time
import subprocess
import shutil
from typing import Dict, Optional
from django.utils import timezone
from apps.vms.models import VirtualMachine
from apps.vms.libvirt_manager import libvirt_manager

logger = logging.getLogger(__name__)

# 用于存储 websockify 进程的全局字典
# 键: websockify_port, 值: subprocess.Popen object
websockify_processes: Dict[int, subprocess.Popen] = {}


class VirtualMachineService:
    """
    虚拟机管理服务
    """
    
    @staticmethod
    def create_vm_sync(vm_id: str) -> Dict:
        """
        同步创建虚拟机
        
        Args:
            vm_id: 虚拟机ID
            
        Returns:
            操作结果
        """
        try:
            vm = VirtualMachine.objects.get(id=vm_id)
            vm.status = 'creating'
            vm.save()
            
            # 检查模板是否存在
            if not vm.template:
                logger.error(f"虚拟机 {vm.name} 没有关联的模板")
                vm.status = 'error'
                vm.save()
                return {'success': False, 'error': '虚拟机没有关联的模板'}
            
            # 生成UUID
            vm_uuid = str(uuid.uuid4())
            
            # 调用libvirt管理器创建虚拟机
            vm_info = libvirt_manager.create_vm(
                name=vm.name,
                uuid=vm_uuid,
                memory_mb=vm.memory_mb,
                cpu_cores=vm.cpu_cores,
                template_path=vm.template.file_path
            )
            
            # 更新虚拟机信息
            vm.uuid = vm_uuid
            vm.mac_address = vm_info['mac_address']
            vm.vnc_port = vm_info['vnc_port']
            vm.vnc_password = vm_info['vnc_password']
            vm.status = 'running'
            vm.save()
            
            logger.info(f"虚拟机 {vm.name} 创建成功")
            return {'success': True, 'vm_id': vm_id}
            
        except VirtualMachine.DoesNotExist:
            logger.error(f"虚拟机不存在: {vm_id}")
            return {'success': False, 'error': '虚拟机不存在'}
        except Exception as e:
            logger.error(f"创建虚拟机失败: {e}")
            try:
                vm = VirtualMachine.objects.get(id=vm_id)
                vm.status = 'error'
                vm.save()
            except:
                pass
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def create_vm_async(vm_id: str):
        """
        异步创建虚拟机（使用线程）
        
        Args:
            vm_id: 虚拟机ID
        """
        def _create():
            VirtualMachineService.create_vm_sync(vm_id)
        
        thread = threading.Thread(target=_create)
        thread.daemon = True
        thread.start()
    
    @staticmethod
    def start_vm(vm_id: str) -> Dict:
        """
        启动虚拟机
        
        Args:
            vm_id: 虚拟机ID
            
        Returns:
            操作结果
        """
        try:
            vm = VirtualMachine.objects.get(id=vm_id)
            
            # 调用libvirt管理器启动虚拟机
            success = libvirt_manager.start_vm(vm.name)
            
            if success:
                vm.status = 'running'
                vm.save()
                logger.info(f"虚拟机 {vm.name} 启动成功")
                return {'success': True, 'vm_id': vm_id}
            else:
                vm.status = 'error'
                vm.save()
                logger.error(f"虚拟机 {vm.name} 启动失败")
                return {'success': False, 'error': '启动失败'}
                
        except VirtualMachine.DoesNotExist:
            logger.error(f"虚拟机不存在: {vm_id}")
            return {'success': False, 'error': '虚拟机不存在'}
        except Exception as e:
            logger.error(f"启动虚拟机失败: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def stop_vm(vm_id: str, force: bool = False) -> Dict:
        """
        停止虚拟机
        
        Args:
            vm_id: 虚拟机ID
            force: 是否强制停止
            
        Returns:
            操作结果
        """
        try:
            vm = VirtualMachine.objects.get(id=vm_id)
            
            # 停止 websockify
            if vm.websockify_port:
                VirtualMachineService.stop_websockify(vm.websockify_port)

            result = libvirt_manager.stop_vm(vm.name, force=force)
            if result:
                vm.status = 'stopped'
                vm.save()
                logger.info(f"虚拟机 {vm.name} 停止成功")
                return {'success': True, 'vm_id': vm_id}
            else:
                logger.error(f"虚拟机 {vm.name} 停止失败")
                return {'success': False, 'error': '停止失败'}
                
        except VirtualMachine.DoesNotExist:
            logger.error(f"虚拟机不存在: {vm_id}")
            return {'success': False, 'error': '虚拟机不存在'}
        except Exception as e:
            logger.error(f"停止虚拟机失败: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def restart_vm(vm_id: str) -> Dict:
        """
        重启虚拟机
        
        Args:
            vm_id: 虚拟机ID
            
        Returns:
            操作结果
        """
        try:
            vm = VirtualMachine.objects.get(id=vm_id)
            
            # 调用libvirt管理器重启虚拟机
            success = libvirt_manager.restart_vm(vm.name)
            
            if success:
                logger.info(f"虚拟机 {vm.name} 重启成功")
                return {'success': True, 'vm_id': vm_id}
            else:
                logger.error(f"虚拟机 {vm.name} 重启失败")
                return {'success': False, 'error': '重启失败'}
                
        except VirtualMachine.DoesNotExist:
            logger.error(f"虚拟机不存在: {vm_id}")
            return {'success': False, 'error': '虚拟机不存在'}
        except Exception as e:
            logger.error(f"重启虚拟机失败: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def pause_vm(vm_id: str) -> Dict:
        """
        暂停虚拟机
        
        Args:
            vm_id: 虚拟机ID
            
        Returns:
            操作结果
        """
        try:
            vm = VirtualMachine.objects.get(id=vm_id)
            
            # 调用libvirt管理器暂停虚拟机
            success = libvirt_manager.pause_vm(vm.name)
            
            if success:
                vm.status = 'paused'
                vm.save()
                logger.info(f"虚拟机 {vm.name} 暂停成功")
                return {'success': True, 'vm_id': vm_id}
            else:
                logger.error(f"虚拟机 {vm.name} 暂停失败")
                return {'success': False, 'error': '暂停失败'}
                
        except VirtualMachine.DoesNotExist:
            logger.error(f"虚拟机不存在: {vm_id}")
            return {'success': False, 'error': '虚拟机不存在'}
        except Exception as e:
            logger.error(f"暂停虚拟机失败: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def resume_vm(vm_id: str) -> Dict:
        """
        恢复虚拟机
        
        Args:
            vm_id: 虚拟机ID
            
        Returns:
            操作结果
        """
        try:
            vm = VirtualMachine.objects.get(id=vm_id)
            
            # 调用libvirt管理器恢复虚拟机
            success = libvirt_manager.resume_vm(vm.name)
            
            if success:
                vm.status = 'running'
                vm.save()
                logger.info(f"虚拟机 {vm.name} 恢复成功")
                return {'success': True, 'vm_id': vm_id}
            else:
                logger.error(f"虚拟机 {vm.name} 恢复失败")
                return {'success': False, 'error': '恢复失败'}
                
        except VirtualMachine.DoesNotExist:
            logger.error(f"虚拟机不存在: {vm_id}")
            return {'success': False, 'error': '虚拟机不存在'}
        except Exception as e:
            logger.error(f"恢复虚拟机失败: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def delete_vm(vm_id: str, remove_disk: bool = True) -> Dict:
        """
        删除虚拟机
        
        Args:
            vm_id: 虚拟机ID
            remove_disk: 是否删除磁盘文件
            
        Returns:
            操作结果
        """
        try:
            vm = VirtualMachine.objects.get(id=vm_id)

            # 停止 websockify
            if vm.websockify_port:
                VirtualMachineService.stop_websockify(vm.websockify_port)

            result = libvirt_manager.delete_vm(vm.name, remove_disk=remove_disk)
            if result:
                # 从数据库中删除记录
                vm.delete()
                logger.info(f"虚拟机 {vm.name} 删除成功")
                return {'success': True, 'vm_id': vm_id}
            else:
                logger.error(f"虚拟机 {vm.name} 删除失败")
                return {'success': False, 'error': '删除失败'}
                
        except VirtualMachine.DoesNotExist:
            logger.error(f"虚拟机不存在: {vm_id}")
            return {'success': False, 'error': '虚拟机不存在'}
        except Exception as e:
            logger.error(f"删除虚拟机失败: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def sync_vm_status() -> Dict:
        """
        同步虚拟机状态
        
        Returns:
            操作结果
        """
        try:
            # 获取libvirt中的所有虚拟机状态
            libvirt_vms = libvirt_manager.list_vms()
            libvirt_vm_names = {vm['name'] for vm in libvirt_vms}
            
            # 获取数据库中的所有虚拟机
            db_vms = VirtualMachine.objects.all()
            
            for vm in db_vms:
                if vm.name in libvirt_vm_names:
                    # 虚拟机存在于libvirt中，同步状态
                    vm_status = libvirt_manager.get_vm_status(vm.name)
                    if vm_status:
                        vm.status = vm_status['state']
                        vm.ip_address = vm_status['ip_address']
                        vm.save()
                else:
                    # 虚拟机不存在于libvirt中，标记为错误状态
                    vm.status = 'error'
                    vm.save()
            
            logger.info("虚拟机状态同步完成")
            return {'success': True, 'synced_count': len(db_vms)}
            
        except Exception as e:
            logger.error(f"同步虚拟机状态失败: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def start_websockify(vm: 'VirtualMachine') -> Optional[int]:
        """为虚拟机启动一个websockify进程"""
        if not vm.vnc_port:
            logger.warning(f"虚拟机 {vm.name} 没有VNC端口，无法启动websockify。")
            return None

        websockify_port = vm.websockify_port
        if websockify_port is None:
            logger.error(f"虚拟机 {vm.name} 的 websockify_port 为 None。")
            return None
            
        vnc_port = vm.vnc_port

        # 检查进程是否已在运行
        if websockify_port in websockify_processes:
            process = websockify_processes[websockify_port]
            if process.poll() is None:  # 进程仍在运行
                logger.info(f"Websockify for port {websockify_port} is already running.")
                return websockify_port
            else:
                logger.info(f"Removing stale websockify process for port {websockify_port}.")
                del websockify_processes[websockify_port]
        
        try:
            # 查找 websockify 的可执行文件路径
            websockify_path = shutil.which('websockify')
            if not websockify_path:
                logger.error("`websockify` command not found. Please ensure it is installed and in the system's PATH.")
                return None

            # 启动新的websockify进程
            command = [
                websockify_path,
                str(websockify_port),
                f'localhost:{vnc_port}'
            ]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            websockify_processes[websockify_port] = process
            logger.info(f"Started websockify for VM {vm.name} on port {websockify_port} (VNC: {vnc_port}). PID: {process.pid}")
            return websockify_port
        except Exception as e:
            logger.error(f"Failed to start websockify for port {websockify_port}: {e}")
            return None

    @staticmethod
    def stop_websockify(websockify_port: int):
        """停止指定的websockify进程"""
        if websockify_port in websockify_processes:
            process = websockify_processes.pop(websockify_port)
            if process.poll() is None: # 进程仍在运行
                process.terminate()
                try:
                    process.wait(timeout=5)
                    logger.info(f"Terminated websockify process on port {websockify_port}. PID: {process.pid}")
                except subprocess.TimeoutExpired:
                    process.kill()
                    logger.warning(f"Killed websockify process on port {websockify_port} as it did not terminate gracefully. PID: {process.pid}")
            else:
                logger.info(f"Websockify process on port {websockify_port} was already stopped.")


# 全局服务实例
vm_service = VirtualMachineService()
