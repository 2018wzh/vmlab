# VMLab 数据模型设计文档

## 概述

本文档定义了VMLab虚拟化实验平台所需的核心数据模型。这些模型基于Django ORM设计，涵盖了用户、课程、虚拟机、任务队列等关键模块。

## 1. 用户模块 (User Module)

### 1.1 `User` (用户模型)
继承自Django的`AbstractUser`，并添加额外字段。

| 字段名 | 类型 | 描述 | 备注 |
|---|---|---|---|
| `id` | `UUIDField` | 主键，用户唯一标识 | 使用UUID避免ID被猜测 |
| `username` | `CharField` | 用户名 | Django自带 |
| `email` | `EmailField` | 邮箱 | Django自带，用于通知和密码重置 |
| `password` | `CharField` | 哈希密码 | Django自带 |
| `first_name` | `CharField` | 名字 | Django自带 |
| `last_name` | `CharField` | 姓氏 | Django自带 |
| `role` | `ForeignKey` | 关联到`Role`模型 | **关键字段**，定义用户角色 |
| `is_active` | `BooleanField` | 是否激活 | Django自带 |
| `is_staff` | `BooleanField` | 是否为员工 | Django自带，控制Admin访问 |
| `date_joined` | `DateTimeField` | 注册时间 | Django自带 |

### 1.2 `Role` (角色模型)
定义系统中的角色。

| 字段名 | 类型 | 描述 | 备注 |
|---|---|---|---|
| `id` | `AutoField` | 主键 | |
| `name` | `CharField` | 角色名称 | 例如: "student", "teacher", "admin" |
| `description` | `TextField` | 角色描述 | |

### 1.3 `Quota` (资源配额模型)
定义每个用户的资源配额。

| 字段名 | 类型 | 描述 | 备注 |
|---|---|---|---|
| `id` | `AutoField` | 主键 | |
| `user` | `OneToOneField` | 关联到`User`模型 | 一对一关系 |
| `cpu_cores` | `IntegerField` | CPU核心数配额 | |
| `memory_mb` | `IntegerField` | 内存配额 (MB) | |
| `disk_gb` | `IntegerField` | 磁盘空间配额 (GB) | |
| `vm_limit` | `IntegerField` | 虚拟机数量限制 | |

## 2. 课程模块 (Course Module)

### 2.1 `Course` (课程模型)

| 字段名 | 类型 | 描述 | 备注 |
|---|---|---|---|
| `id` | `AutoField` | 主键 | |
| `name` | `CharField` | 课程名称 | |
| `description` | `TextField` | 课程描述 | |
| `teachers` | `ManyToManyField` | 关联到`User`模型 | 授课教师 |
| `students` | `ManyToManyField` | 关联到`User`模型 | 选课学生 |
| `created_at` | `DateTimeField` | 创建时间 | |
| `updated_at` | `DateTimeField` | 更新时间 | |

### 2.2 `VirtualMachineTemplate` (虚拟机模板模型)
教师上传的虚拟机磁盘镜像。

| 字段名 | 类型 | 描述 | 备注 |
|---|---|---|---|
| `id` | `AutoField` | 主键 | |
| `name` | `CharField` | 模板名称 | |
| `description` | `TextField` | 模板描述 | |
| `file_path` | `CharField` | qcow2文件路径 | 存储在服务器上的路径 |
| `owner` | `ForeignKey` | 关联到`User`模型 | 上传者（教师） |
| `course` | `ForeignKey` | 关联到`Course`模型 | 模板所属课程 |
| `is_public` | `BooleanField` | 是否公开 | 公开模板所有课程可用 |
| `created_at` | `DateTimeField` | 创建时间 | |

## 3. 虚拟机模块 (Virtual Machine Module)

### 3.1 `VirtualMachine` (虚拟机模型)

| 字段名 | 类型 | 描述 | 备注 |
|---|---|---|---|
| `id` | `UUIDField` | 主键 | |
| `name` | `CharField` | 虚拟机名称 | |
| `uuid` | `CharField` | Libvirt中的UUID | 用于与底层虚拟化层交互 |
| `owner` | `ForeignKey` | 关联到`User`模型 | 虚拟机所有者（学生） |
| `course` | `ForeignKey` | 关联到`Course`模型 | 所属课程 |
| `template` | `ForeignKey` | 关联到`VirtualMachineTemplate` | 创建时使用的模板 |
| `cpu_cores` | `IntegerField` | CPU核心数 | |
| `memory_mb` | `IntegerField` | 内存大小 (MB) | |
| `disk_gb` | `IntegerField` | 磁盘大小 (GB) | |
| `status` | `CharField` | 虚拟机状态 | "creating", "stopped", "running", "paused", "error", "deleting" |
| `ip_address` | `GenericIPAddressField` | IP地址 | |
| `mac_address` | `CharField` | MAC地址 | |
| `vnc_port` | `IntegerField` | VNC端口 | |
| `vnc_password` | `CharField` | VNC密码 | |
| `created_at` | `DateTimeField` | 创建时间 | |
| `updated_at` | `DateTimeField` | 更新时间 | |
