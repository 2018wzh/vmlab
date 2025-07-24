"""
Libvirt虚拟机管理器
"""
import libvirt
import xml.etree.ElementTree as ET
import random
import string
import logging
import time
import os
from typing import Any, Dict, List, Optional, Tuple
from django.conf import settings

logger = logging.getLogger(__name__)

class LibvirtManager:
    """
    Libvirt虚拟机管理器
    """
    # conn 属性在运行时由 libvirt.open 初始化
    conn: Any
    
    def __init__(self, uri: str = "qemu:///system"):
        """
        初始化Libvirt连接
        
        Args:
            uri: Libvirt连接URI
        """
        self.uri = uri
        self.conn = None
        if not os.environ.get('DOCKER_BUILDING'):
            self._connect()
    
    def _connect(self):
        """建立Libvirt连接"""
        try:
            self.conn = libvirt.open(self.uri)
            if self.conn is None:
                raise Exception(f"无法连接到libvirt: {self.uri}")
            logger.info(f"成功连接到libvirt: {self.uri}")
        except libvirt.libvirtError as e:
            logger.error(f"连接libvirt失败: {e}")
            raise
    
    def _ensure_connection(self):
        """确保连接有效"""
        if self.conn is None or not self.conn.isAlive():
            self._connect()
    
    def _generate_vm_xml(self, name: str, uuid: str, memory_mb: int, 
                        cpu_cores: int, disk_path: str, vnc_port: int,
                        mac_address: str, vnc_password: str) -> str:
        """
        生成虚拟机XML配置
        
        Args:
            name: 虚拟机名称
            uuid: UUID
            memory_mb: 内存大小(MB)
            cpu_cores: CPU核心数
            disk_path: 磁盘文件路径
            vnc_port: VNC端口
            mac_address: MAC地址
            
        Returns:
            XML配置字符串
        """
        xml_template = f"""
<domain type='kvm'>
  <name>{name}</name>
  <uuid>{uuid}</uuid>
  <memory unit='MiB'>{memory_mb}</memory>
  <currentMemory unit='MiB'>{memory_mb}</currentMemory>
  <vcpu>{cpu_cores}</vcpu>
  <os>
    <type arch='x86_64'>hvm</type>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <apic/>
    <pae/>
  </features>
  <clock offset='utc'/>
  <devices>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='{disk_path}'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    <interface type='network'>
      <source network='default'/>
      <mac address='{mac_address}'/>
      <model type='virtio'/>
    </interface>
    <graphics type='vnc' port='{vnc_port}' autoport='no' listen='0.0.0.0'>
      <listen type='address' address='0.0.0.0'/>
      <passwd>{vnc_password}</passwd>
    </graphics>
    <video>
      <model type='cirrus'/>
    </video>
    <console type='pty'>
      <target type='virtio' port='0'/>
    </console>
    <serial type='pty'>
      <target port='0'/>
    </serial>
  </devices>
</domain>
        """.strip()
        return xml_template
    
    def _generate_mac_address(self) -> str:
        """生成随机MAC地址"""
        # 使用52:54:00前缀（QEMU/KVM保留）
        mac = "52:54:00"
        for _ in range(3):
            mac += ":" + "".join(random.choices(string.hexdigits.lower(), k=2))
        return mac
    
    def _find_available_vnc_port(self) -> int:
        """找到可用的VNC端口"""
        # 从5900开始查找可用端口
        for port in range(5900, 6000):
            if self._is_port_available(port):
                return port
        raise Exception("无法找到可用的VNC端口")

    
    def _generate_vnc_password(self, length: int = 8) -> str:
        """生成随机VNC密码"""
        import random, string
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def _is_port_available(self, port: int) -> bool:
        """检查端口是否可用"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('localhost', port))
            return result != 0
    
    def create_vm(self, name: str, uuid: str, memory_mb: int, cpu_cores: int,
                  template_path: str, storage_dir: str = "/var/lib/libvirt/images") -> Dict:
        """
        创建虚拟机
        
        Args:
            name: 虚拟机名称
            uuid: UUID
            memory_mb: 内存大小 (MB)
            cpu_cores: CPU核心数
            template_path: 模板文件路径
            storage_dir: 存储目录

        Returns:
            包含虚拟机信息的字典
        """
        self._ensure_connection()
        
        try:
            # 检查虚拟机是否已存在
            try:
                existing_vm = self.conn.lookupByName(name)
                if existing_vm:
                    raise Exception(f"虚拟机 {name} 已存在")
            except libvirt.libvirtError:
                # 虚拟机不存在，继续创建
                pass
            
            # 生成配置
            mac_address = self._generate_mac_address()
            vnc_port = self._find_available_vnc_port()
            vnc_password = self._generate_vnc_password()
            
            # 创建虚拟机磁盘
            disk_path = f"{storage_dir}/{name}.qcow2"
            self._create_vm_disk(template_path, disk_path)
            
            # 生成XML配置，包含VNC密码
            xml_config = self._generate_vm_xml(
                name=name,
                uuid=uuid,
                memory_mb=memory_mb,
                cpu_cores=cpu_cores,
                disk_path=disk_path,
                vnc_port=vnc_port,
                mac_address=mac_address,
                vnc_password=vnc_password
            )
            
            # 定义并启动虚拟机
            domain = self.conn.defineXML(xml_config)
            try:
                result = domain.create()
                if result != 0:
                    raise Exception(f"启动虚拟机 {name} 失败, 返回码: {result}")
            except libvirt.libvirtError as e:
                logger.error(f"启动虚拟机失败: {e}")
                raise
            logger.info(f"虚拟机 {name} 创建并启动成功")

            return {
                'name': name,
                'uuid': uuid,
                'mac_address': mac_address,
                'vnc_port': vnc_port,
                'vnc_password': vnc_password,
                'disk_path': disk_path,
                'status': 'running'
            }
            
        except Exception as e:
            logger.error(f"创建虚拟机失败: {e}")
            raise
    
    def _create_vm_disk(self, template_path: str, disk_path: str):
        """
        从模板创建虚拟机磁盘
        
        Args:
            template_path: 模板文件路径
            disk_path: 目标磁盘路径
        """
        import shutil
        import os
        
        if not os.path.exists(template_path):
            raise Exception(f"模板文件不存在: {template_path}")
        
        # 复制模板文件
        shutil.copy2(template_path, disk_path)
        logger.info(f"从模板 {template_path} 创建磁盘 {disk_path}")
    
    def start_vm(self, name: str) -> bool:
        """
        启动虚拟机
        
        Args:
            name: 虚拟机名称
            
        Returns:
            操作是否成功
        """
        self._ensure_connection()
        # 确保连接已建立，用于类型检查
        assert self.conn is not None

        # 检查虚拟机是否存在
        try:
            domain = self.conn.lookupByName(name)
        except libvirt.libvirtError as e:
            logger.error(f"虚拟机 {name} 不存在: {e}")
            raise Exception(f"虚拟机 {name} 不存在")

        # 如果已经在运行，直接返回
        if domain.isActive():
            logger.warning(f"虚拟机 {name} 已经在运行")
            return True

        # 启动虚拟机
        try:
            result = domain.create()
        except libvirt.libvirtError as e:
            logger.error(f"启动虚拟机失败: {e}")
            raise Exception(f"启动虚拟机失败: {e}")
        # 启动结果检查
        if result == 0:
            logger.info(f"虚拟机 {name} 启动成功")
            return True
        else:
            logger.error(f"虚拟机 {name} 启动失败, 返回码: {result}")
            raise Exception(f"虚拟机 {name} 启动失败, 返回码: {result}")
    
    def stop_vm(self, name: str, force: bool = False) -> bool:
        """
        停止虚拟机
        
        Args:
            name: 虚拟机名称
            force: 是否强制停止
            
        Returns:
            操作是否成功
        """
        self._ensure_connection()
        
        try:
            domain = self.conn.lookupByName(name)
            if not domain.isActive():
                logger.warning(f"虚拟机 {name} 已经停止")
                return True
            
            if force:
                result = domain.destroy()
            else:
                result = domain.shutdown()
            
            if result == 0:
                logger.info(f"虚拟机 {name} 停止成功")
                return True
            else:
                logger.error(f"虚拟机 {name} 停止失败")
                return False
                
        except libvirt.libvirtError as e:
            logger.error(f"停止虚拟机失败: {e}")
            return False
    
    def restart_vm(self, name: str) -> bool:
        """
        重启虚拟机
        
        Args:
            name: 虚拟机名称
            
        Returns:
            操作是否成功
        """
        self._ensure_connection()
        
        try:
            domain = self.conn.lookupByName(name)
            result = domain.reboot()
            
            if result == 0:
                logger.info(f"虚拟机 {name} 重启成功")
                return True
            else:
                logger.error(f"虚拟机 {name} 重启失败")
                return False
                
        except libvirt.libvirtError as e:
            logger.error(f"重启虚拟机失败: {e}")
            return False
    
    def pause_vm(self, name: str) -> bool:
        """
        暂停虚拟机
        
        Args:
            name: 虚拟机名称
            
        Returns:
            操作是否成功
        """
        self._ensure_connection()
        
        try:
            domain = self.conn.lookupByName(name)
            result = domain.suspend()
            
            if result == 0:
                logger.info(f"虚拟机 {name} 暂停成功")
                return True
            else:
                logger.error(f"虚拟机 {name} 暂停失败")
                return False
                
        except libvirt.libvirtError as e:
            logger.error(f"暂停虚拟机失败: {e}")
            return False
    
    def resume_vm(self, name: str) -> bool:
        """
        恢复虚拟机
        
        Args:
            name: 虚拟机名称
            
        Returns:
            操作是否成功
        """
        self._ensure_connection()
        
        try:
            domain = self.conn.lookupByName(name)
            result = domain.resume()
            
            if result == 0:
                logger.info(f"虚拟机 {name} 恢复成功")
                return True
            else:
                logger.error(f"虚拟机 {name} 恢复失败")
                return False
                
        except libvirt.libvirtError as e:
            logger.error(f"恢复虚拟机失败: {e}")
            return False
    
    def delete_vm(self, name: str, remove_disk: bool = True) -> bool:
        """
        删除虚拟机
        
        Args:
            name: 虚拟机名称
            remove_disk: 是否删除磁盘文件
            
        Returns:
            操作是否成功
        """
        self._ensure_connection()
        
        try:
            domain = self.conn.lookupByName(name)
            
            # 获取磁盘路径
            disk_path = None
            if remove_disk:
                xml_desc = domain.XMLDesc()
                root = ET.fromstring(xml_desc)
                disk_elem = root.find(".//disk[@type='file']/source")
                if disk_elem is not None:
                    disk_path = disk_elem.get('file')
            
            # 停止虚拟机（如果正在运行）
            if domain.isActive():
                domain.destroy()
            
            # 取消定义虚拟机
            result = domain.undefine()
            
            # 删除磁盘文件
            if remove_disk and disk_path:
                import os
                try:
                    os.remove(disk_path)
                    logger.info(f"删除磁盘文件: {disk_path}")
                except OSError as e:
                    logger.warning(f"删除磁盘文件失败: {e}")
            
            if result == 0:
                logger.info(f"虚拟机 {name} 删除成功")
                return True
            else:
                logger.error(f"虚拟机 {name} 删除失败")
                return False
                
        except libvirt.libvirtError as e:
            logger.error(f"删除虚拟机失败: {e}")
            return False
    
    def get_vm_status(self, name: str) -> Optional[Dict]:
        """
        获取虚拟机状态
        
        Args:
            name: 虚拟机名称
            
        Returns:
            虚拟机状态信息字典
        """
        self._ensure_connection()
        
        try:
            domain = self.conn.lookupByName(name)
            state, reason = domain.state()
            
            # 状态映射
            state_map = {
                libvirt.VIR_DOMAIN_NOSTATE: 'nostate',
                libvirt.VIR_DOMAIN_RUNNING: 'running',
                libvirt.VIR_DOMAIN_BLOCKED: 'blocked',
                libvirt.VIR_DOMAIN_PAUSED: 'paused',
                libvirt.VIR_DOMAIN_SHUTDOWN: 'shutdown',
                libvirt.VIR_DOMAIN_SHUTOFF: 'stopped',
                libvirt.VIR_DOMAIN_CRASHED: 'crashed',
                libvirt.VIR_DOMAIN_PMSUSPENDED: 'suspended',
            }
            
            # 获取VNC信息
            vnc_port = None
            xml_desc = domain.XMLDesc()
            root = ET.fromstring(xml_desc)
            graphics_elem = root.find(".//graphics[@type='vnc']")
            if graphics_elem is not None:
                vnc_port = graphics_elem.get('port')
            
            # 获取IP地址
            ip_address = None
            try:
                ifaces = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)
                for iface_name, iface_info in ifaces.items():
                    for addr in iface_info['addrs']:
                        if addr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                            ip_address = addr['addr']
                            break
            except:
                pass
            
            return {
                'name': name,
                'state': state_map.get(state, 'unknown'),
                'vnc_port': vnc_port,
                'ip_address': ip_address,
                'is_active': domain.isActive() == 1
            }
            
        except libvirt.libvirtError as e:
            logger.error(f"获取虚拟机状态失败: {e}")
            return None
    
    def get_vm_metrics(self, name: str) -> Optional[Dict]:
        """
        获取虚拟机监控指标
        
        Args:
            name: 虚拟机名称
            
        Returns:
            监控指标字典
        """
        self._ensure_connection()
        
        try:
            domain = self.conn.lookupByName(name)
            
            if not domain.isActive():
                return {
                    'cpu_usage': 0,
                    'memory_usage': 0,
                    'disk_usage': 0,
                    'network_rx': 0,
                    'network_tx': 0
                }
            
            # 获取CPU统计
            cpu_stats = domain.getCPUStats(True)
            
            # 获取内存统计
            memory_stats = domain.memoryStats()
            
            # 获取磁盘统计
            disk_stats = {}
            try:
                disk_stats = domain.blockStats('vda')
            except:
                pass
            
            # 获取网络统计
            network_stats = {}
            try:
                xml_desc = domain.XMLDesc()
                root = ET.fromstring(xml_desc)
                interface_elem = root.find(".//interface[@type='network']/target")
                if interface_elem is not None:
                    dev_name = interface_elem.get('dev')
                    if dev_name:
                        network_stats = domain.interfaceStats(dev_name)
            except:
                pass
            
            return {
                'cpu_usage': cpu_stats[0].get('cpu_time', 0) if cpu_stats else 0,
                'memory_usage': memory_stats.get('actual', 0),
                'memory_available': memory_stats.get('usable', 0),
                'disk_read': disk_stats[1] if disk_stats else 0,
                'disk_write': disk_stats[3] if disk_stats else 0,
                'network_rx': network_stats[0] if network_stats else 0,
                'network_tx': network_stats[4] if network_stats else 0,
            }
            
        except libvirt.libvirtError as e:
            logger.error(f"获取虚拟机监控指标失败: {e}")
            return None
    
    def list_vms(self) -> List[Dict]:
        """
        列出所有虚拟机
        
        Returns:
            虚拟机列表
        """
        self._ensure_connection()
        
        try:
            vms = []
            
            # 获取所有定义的虚拟机
            for domain_id in self.conn.listDefinedDomains():
                domain = self.conn.lookupByName(domain_id)
                vm_info = self.get_vm_status(domain_id)
                if vm_info:
                    vms.append(vm_info)
            
            # 获取所有运行中的虚拟机
            for domain_id in self.conn.listDomainsID():
                domain = self.conn.lookupByID(domain_id)
                vm_info = self.get_vm_status(domain.name())
                if vm_info and vm_info not in vms:
                    vms.append(vm_info)
            
            return vms
            
        except libvirt.libvirtError as e:
            logger.error(f"列出虚拟机失败: {e}")
            return []
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            self.conn = None


# 全局管理器实例
libvirt_manager = LibvirtManager()
