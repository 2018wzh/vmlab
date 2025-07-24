# VMLab API 接口设计文档

## 概述

VMLab虚拟化实验平台API设计遵循RESTful风格，提供完整的虚拟机管理、用户管理、课程管理等功能接口。所有API响应均采用JSON格式，支持基于角色的权限控制、资源配额管理和实时虚拟机监控。

### 主要特性
- **基于角色的权限控制**: 支持学生、教师、管理员三种角色
- **资源配额管理**: CPU、内存、磁盘、虚拟机数量配额控制
- **课程隔离**: 虚拟机与课程关联，权限隔离
- **实时监控**: 虚拟机状态和性能指标实时获取
- **异步任务**: 虚拟机创建等耗时操作采用异步处理
- **VNC控制台**: 支持Web VNC访问虚拟机控制台

## 基础信息

- **Base URL**: `/api/`
- **认证方式**: JWT Token (Bearer Token)
- **内容类型**: `application/json`
- **字符编码**: `UTF-8`

## API路由总览

### 用户相关路由
- `/api/users/` - 用户管理
- `/api/roles/` - 角色管理
- `/api/auth/register/` - 用户注册
- `/api/auth/login/` - 用户登录
- `/api/auth/refresh/` - Token刷新
- `/api/auth/user/profile/` - 用户个人资料

### 课程相关路由
- `/api/courses/` - 课程管理
- `/api/templates/` - 虚拟机模板管理

### 虚拟机相关路由
- `/api/vms/` - 虚拟机管理

### 系统路由
- `/health/` - 健康检查

## 通用响应格式

### 成功响应
```json
{
    "success": true,
    "data": {},
    "message": "操作成功",
    "timestamp": "2025-07-23T10:30:00Z"
}
```

### 错误响应
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "错误描述",
        "details": {}
    },
    "timestamp": "2025-07-23T10:30:00Z"
}
```

### 分页响应
```json
{
    "success": true,
    "data": {
        "results": [],
        "pagination": {
            "page": 1,
            "page_size": 20,
            "total": 100,
            "total_pages": 5,
            "has_next": true,
            "has_previous": false
        }
    },
    "message": "查询成功"
}
```

## 1. 用户认证模块

### 1.1 用户认证
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/auth/login/` | 用户登录 (JWT Token) |
| POST | `/auth/refresh/` | 刷新Token |
| POST | `/auth/register/` | 用户注册 |

### 1.2 用户信息
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/auth/user/profile/` | 获取当前用户信息 |
| PUT | `/auth/user/profile/` | 更新用户信息 |

## 2. 用户管理模块

### 2.1 用户CRUD
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/users/` | 获取用户列表 |
| POST | `/users/` | 创建用户 |
| GET | `/users/{id}/` | 获取用户详情 |
| PUT | `/users/{id}/` | 更新用户信息 |
| PATCH | `/users/{id}/` | 部分更新用户信息 |
| DELETE | `/users/{id}/` | 删除用户 |

### 2.2 用户角色管理
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/users/{id}/roles/` | 获取用户角色 |
| POST | `/users/{id}/roles/` | 分配角色 |
| GET | `/roles/` | 获取所有角色 |

### 2.3 用户资源配额
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/users/{id}/quota/` | 获取用户配额信息 |
| PUT | `/users/{id}/quota/` | 更新用户配额 |

### 2.4 配额使用情况 (虚拟实现)
> 注意：配额使用情况在虚拟机创建时进行检查，目前没有单独的API endpoint，但可以通过用户配额API获取配额信息，使用情况需要通过查询该用户的虚拟机来计算。

## 3. 课程管理模块

### 3.1 课程CRUD
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/courses/` | 获取课程列表 |
| POST | `/courses/` | 创建课程 |
| GET | `/courses/{id}/` | 获取课程详情 |
| PUT | `/courses/{id}/` | 更新课程信息 |
| PATCH | `/courses/{id}/` | 部分更新课程信息 |
| DELETE | `/courses/{id}/` | 删除课程 |

### 3.2 课程成员管理
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/courses/{id}/students/` | 获取课程学生列表 |
| POST | `/courses/{id}/add_student/` | 添加学生到课程 |
| DELETE | `/courses/{id}/students/{user_id}/` | 从课程移除学生 |
| GET | `/courses/{id}/teachers/` | 获取课程教师列表 |
| POST | `/courses/{id}/add_teacher/` | 添加教师到课程 |
| DELETE | `/courses/{id}/teachers/{user_id}/` | 从课程移除教师 |

### 3.3 虚拟机模板管理
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/courses/{id}/templates/` | 获取课程模板列表 |
| POST | `/courses/{id}/add_template/` | 为课程添加虚拟机模板 |
| GET | `/templates/` | 获取模板列表 |
| POST | `/templates/` | 创建虚拟机模板 |
| GET | `/templates/{id}/` | 获取模板详情 |
| PUT | `/templates/{id}/` | 更新模板信息 |
| DELETE | `/templates/{id}/` | 删除模板 |
| POST | `/templates/{id}/validate/` | 验证模板文件 |

### 3.4 课程统计
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/courses/{id}/statistics/` | 获取课程统计信息 |

## 4. 虚拟机管理模块

### 4.1 虚拟机CRUD
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/vms/` | 获取虚拟机列表 |
| POST | `/vms/` | 创建虚拟机 |
| GET | `/vms/{id}/` | 获取虚拟机详情 |
| PUT | `/vms/{id}/` | 更新虚拟机配置 |
| DELETE | `/vms/{id}/` | 删除虚拟机 |

### 4.2 虚拟机操作
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/vms/{id}/start/` | 启动虚拟机 |
| POST | `/vms/{id}/stop/` | 停止虚拟机 |
| POST | `/vms/{id}/restart/` | 重启虚拟机 |
| POST | `/vms/{id}/pause/` | 暂停虚拟机 |
| POST | `/vms/{id}/resume/` | 恢复虚拟机 |

### 4.3 虚拟机状态和监控
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/vms/{id}/status/` | 获取虚拟机状态 |
| GET | `/vms/{id}/metrics/` | 获取虚拟机监控指标 |

### 4.4 控制台访问
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/vms/{id}/console_vnc/` | 获取VNC控制台访问信息 |
|
### 4.5 转换为模板
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/vms/{id}/convert_to_template/` | 将虚拟机转换为模板 |

## 5. 健康检查

### 5.1 系统健康检查
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/health/` | 系统健康检查 |

## 详细API接口说明

### 虚拟机创建请求格式
```json
{
  "name": "ubuntu-vm-001",
  "template_id": "550e8400-e29b-41d4-a716-446655440000",
  "cpu_cores": 2,
  "memory_mb": 2048,
  "disk_gb": 20,
  "course_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

### 虚拟机列表响应格式
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "ubuntu-vm-001",
      "uuid": "vm-uuid-string",
      "owner": "550e8400-e29b-41d4-a716-446655440002",
      "owner_username": "student1",
      "course": "550e8400-e29b-41d4-a716-446655440001",
      "course_name": "计算机系统原理",
      "template": "550e8400-e29b-41d4-a716-446655440003",
      "template_name": "Ubuntu 20.04",
      "cpu_cores": 2,
      "memory_mb": 2048,
      "disk_gb": 20,
      "status": "running",
      "ip_address": "192.168.1.100",
      "mac_address": "52:54:00:12:34:56",
      "vnc_port": 5900,
      "created_at": "2025-07-23T10:30:00Z",
      "updated_at": "2025-07-23T10:30:00Z"
    }
  ]
}
```

### 虚拟机状态响应格式
```json
{
  "success": true,
  "data": {
    "name": "ubuntu-vm-001",
    "state": "running",
    "vnc_port": "5900",
    "ip_address": "192.168.1.100",
    "is_active": true
  }
}
```

### 虚拟机监控指标响应格式
```json
{
  "success": true,
  "data": {
    "cpu_usage": 45,
    "memory_usage": 1024,
    "memory_available": 1024,
    "disk_read": 1048576,
    "disk_write": 524288,
    "network_rx": 1048576,
    "network_tx": 524288
  }
}
```

### VNC控制台访问响应格式
```json
{
  "success": true,
  "data": {
    "vnc_url": "ws://localhost:5900",
    "vnc_port": 5900,
    "vnc_password": "randompassword"
  }
}
```

### 课程统计信息响应格式
```json
{
  "success": true,
  "data": {
    "total_students": 25,
    "total_teachers": 2,
    "total_templates": 3,
    "total_vms": 18,
    "running_vms": 12,
    "stopped_vms": 6
  }
}
```

### 用户配额信息响应格式
```json
{
  "success": true,
  "data": {
    "cpu_cores": 8,
    "memory_mb": 8192,
    "disk_gb": 100,
    "vm_limit": 5
  }
}
```

## 重要说明与限制

### 认证与授权
- 所有API（除注册和登录外）都需要JWT Token认证
- Token通过`Authorization: Bearer <token>`头部传递
- 用户权限基于角色系统：student（学生）、teacher（教师）、admin（管理员）

### 资源配额
- 每个用户都有CPU、内存、磁盘和虚拟机数量限制
- 创建虚拟机时会自动检查配额限制
- 配额不足时创建操作会失败并返回详细错误信息

### 虚拟机管理
- 虚拟机创建是异步操作，创建请求成功不等于虚拟机创建完成
- 学生只能管理自己的虚拟机
- 教师可以管理自己课程中学生的虚拟机
- 管理员可以管理所有虚拟机

### 课程权限
- 学生只能访问自己选修的课程
- 教师可以管理自己教授的课程
- 只有教师和管理员可以创建课程和上传模板

### UUID格式
- 用户ID、虚拟机ID、模板ID等都使用UUID格式
- 课程ID使用自增整数

## API 使用示例

### 创建虚拟机
```bash
curl -X POST "http://localhost:8000/api/vms/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ubuntu-vm-001",
    "template_id": "550e8400-e29b-41d4-a716-446655440000",
    "cpu_cores": 2,
    "memory_mb": 2048,
    "disk_gb": 20,
    "course_id": "550e8400-e29b-41d4-a716-446655440001"
  }'
```

### 启动虚拟机
```bash
curl -X POST "http://localhost:8000/api/vms/550e8400-e29b-41d4-a716-446655440000/start/" \
  -H "Authorization: Bearer <token>"
```

### 获取虚拟机状态
```bash
curl -X GET "http://localhost:8000/api/vms/550e8400-e29b-41d4-a716-446655440000/status/" \
  -H "Authorization: Bearer <token>"
```

### 获取虚拟机监控数据
```bash
curl -X GET "http://localhost:8000/api/vms/550e8400-e29b-41d4-a716-446655440000/metrics/" \
  -H "Authorization: Bearer <token>"
```

### 用户注册
```bash
curl -X POST "http://localhost:8000/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepassword123",
    "password2": "securepassword123",
    "email": "newuser@example.com",
    "first_name": "New",
    "last_name": "User"
  }'
```

### 用户登录
```bash
curl -X POST "http://localhost:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepassword123"
  }'
```

### 创建课程
```bash
curl -X POST "http://localhost:8000/api/courses/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "计算机系统原理",
    "description": "学习计算机系统基础知识"
  }'
```

### 添加学生到课程
```bash
curl -X POST "http://localhost:8000/api/courses/1/add_student/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "550e8400-e29b-41d4-a716-446655440002"
  }'
```

## 错误码说明

| 错误码 | HTTP状态码 | 描述 | 详细说明 |
|--------|-----------|------|----------|
| AUTH_001 | 401 | 未授权访问 | Token无效或已过期 |
| AUTH_002 | 403 | 权限不足 | 用户无权访问此资源 |
| VALIDATION_001 | 400 | 参数验证失败 | 请求参数格式或内容错误 |
| RESOURCE_001 | 404 | 资源不存在 | 请求的资源不存在 |
| QUOTA_001 | 400 | 配额不足 | CPU、内存或磁盘配额不足 |
| VM_001 | 500 | 虚拟机操作失败 | 虚拟机创建、启动、停止等操作失败 |
| PERMISSION_001 | 403 | 操作权限不足 | 用户无权进行此操作 |

### 常见错误响应示例

#### 配额不足错误
```json
{
  "success": false,
  "error": {
    "code": "QUOTA_001",
    "message": "CPU配额不足，当前已使用4核，配额4核",
    "details": {
      "used_cpu": 4,
      "quota_cpu": 4,
      "requested_cpu": 2
    }
  },
  "timestamp": "2025-07-23T10:30:00Z"
}
```

#### 权限不足错误
```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_001",
    "message": "您没有权限操作此虚拟机",
    "details": {}
  },
  "timestamp": "2025-07-23T10:30:00Z"
}
```

#### 参数验证失败
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_001",
    "message": "参数验证失败",
    "details": {
      "template_id": ["此字段为必填项。"],
      "cpu_cores": ["确保该值大于或等于 1。"]
    }
  },
  "timestamp": "2025-07-23T10:30:00Z"
}
```
