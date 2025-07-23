# VMLab API 接口设计文档

## 概述

VMLab虚拟化实验平台API设计遵循RESTful风格，提供完整的虚拟机管理、用户管理、课程管理等功能接口。所有API响应均采用JSON格式，支持分页、过滤、排序等功能。

## 基础信息

- **Base URL**: `/api/v1/`
- **认证方式**: JWT Token / Session Authentication
- **内容类型**: `application/json`
- **字符编码**: `UTF-8`

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
| POST | `/auth/login/` | 用户登录 |
| POST | `/auth/logout/` | 用户登出 |
| POST | `/auth/refresh/` | 刷新Token |
| POST | `/auth/register/` | 用户注册 |
| POST | `/auth/password/reset/` | 密码重置请求 |
| POST | `/auth/password/reset/confirm/` | 密码重置确认 |
| POST | `/auth/password/change/` | 修改密码 |

### 1.2 用户信息
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/auth/user/profile/` | 获取当前用户信息 |
| PUT | `/auth/user/profile/` | 更新用户信息 |
| POST | `/auth/user/avatar/` | 上传用户头像 |

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
| DELETE | `/users/{id}/roles/{role_id}/` | 移除角色 |
| GET | `/roles/` | 获取所有角色 |

### 2.3 用户资源配额
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/users/{id}/quota/` | 获取用户配额信息 |
| PUT | `/users/{id}/quota/` | 更新用户配额 |
| GET | `/users/{id}/quota/usage/` | 获取配额使用情况 |

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
| POST | `/courses/{id}/students/` | 添加学生到课程 |
| DELETE | `/courses/{id}/students/{user_id}/` | 从课程移除学生 |
| GET | `/courses/{id}/teachers/` | 获取课程教师列表 |
| POST | `/courses/{id}/teachers/` | 添加教师到课程 |
| DELETE | `/courses/{id}/teachers/{user_id}/` | 从课程移除教师 |

### 3.3 虚拟机模板管理
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/courses/{id}/templates/` | 获取课程模板列表 |
| POST | `/courses/{id}/templates/` | 上传虚拟机模板 |
| GET | `/templates/{id}/` | 获取模板详情 |
| PUT | `/templates/{id}/` | 更新模板信息 |
| DELETE | `/templates/{id}/` | 删除模板 |
| POST | `/templates/{id}/validate/` | 验证模板文件 |

### 3.4 课程统计
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/courses/{id}/statistics/` | 获取课程统计信息 |
| GET | `/courses/{id}/vm-usage/` | 获取虚拟机使用统计 |
| GET | `/courses/{id}/student-activity/` | 获取学生活动统计 |

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
| POST | `/vms/{id}/reset/` | 重置虚拟机 |

### 4.3 虚拟机状态和监控
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/vms/{id}/status/` | 获取虚拟机状态 |
| GET | `/vms/{id}/metrics/` | 获取虚拟机监控指标 |
| GET | `/vms/{id}/metrics/history/` | 获取历史监控数据 |
| GET | `/vms/{id}/logs/` | 获取虚拟机日志 |

### 4.4 控制台访问
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/vms/{id}/console/vnc/` | 获取VNC控制台访问信息 |
| GET | `/vms/{id}/console/ssh/` | 获取SSH控制台访问信息 |
| POST | `/vms/{id}/console/vnc/token/` | 生成VNC访问令牌 |
| POST | `/vms/{id}/console/ssh/token/` | 生成SSH访问令牌 |
## 5. 任务队列模块

### 5.1 任务管理
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/tasks/` | 获取任务列表 |
| GET | `/tasks/{id}/` | 获取任务详情 |
| POST | `/tasks/{id}/cancel/` | 取消任务 |
| POST | `/tasks/{id}/retry/` | 重试任务 |

### 5.2 任务监控
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/tasks/status/` | 获取任务队列状态 |
| GET | `/tasks/workers/` | 获取工作进程状态 |
| GET | `/tasks/statistics/` | 获取任务统计信息 |

## 6. 文件管理模块

### 6.1 文件上传
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/files/upload/` | 文件上传 |
| POST | `/files/upload/chunk/` | 分片上传 |
| POST | `/files/upload/merge/` | 合并分片 |

### 6.2 文件管理
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/files/` | 获取文件列表 |
| GET | `/files/{id}/` | 获取文件信息 |
| GET | `/files/{id}/download/` | 下载文件 |
| DELETE | `/files/{id}/` | 删除文件 |

## API 使用示例

### 创建虚拟机
```bash
curl -X POST "http://localhost:8000/api/v1/vms/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ubuntu-vm-001",
    "template_id": 1,
    "cpu_cores": 2,
    "memory_mb": 2048,
    "disk_gb": 20,
    "course_id": 1
  }'
```

### 启动虚拟机
```bash
curl -X POST "http://localhost:8000/api/v1/vms/1/start/" \
  -H "Authorization: Bearer <token>"
```

### 获取虚拟机监控数据
```bash
curl -X GET "http://localhost:8000/api/v1/vms/1/metrics/?start_time=2025-07-23T00:00:00Z&end_time=2025-07-23T23:59:59Z" \
  -H "Authorization: Bearer <token>"
```

## 错误码说明

| 错误码 | HTTP状态码 | 描述 |
|--------|-----------|------|
| AUTH_001 | 401 | 未授权访问 |
| AUTH_002 | 403 | 权限不足 |
| VALIDATION_001 | 400 | 参数验证失败 |
| RESOURCE_001 | 404 | 资源不存在 |
| QUOTA_001 | 400 | 配额不足 |
| VM_001 | 500 | 虚拟机操作失败 |
| TASK_001 | 500 | 任务执行失败 |
