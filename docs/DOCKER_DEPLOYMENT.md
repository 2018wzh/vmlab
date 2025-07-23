# VMLab Docker 部署指南

本文档描述如何使用Docker容器化部署VMLab虚拟化实验平台。

## 系统要求

### 硬件要求
- CPU: 支持虚拟化扩展的多核处理器
- 内存: 至少8GB RAM
- 存储: 至少50GB可用空间
- 网络: 稳定的网络连接

### 软件要求
- Linux操作系统（推荐Ubuntu 20.04+）
- Docker CE 20.10+
- Docker Compose 1.29+
- Libvirt/KVM（用于虚拟化）

## 快速开始

### 1. 安装依赖

```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 安装libvirt
sudo apt-get update
sudo apt-get install -y libvirt-daemon-system libvirt-clients qemu-kvm
sudo systemctl enable --now libvirtd
sudo usermod -a -G libvirt $USER
```

### 2. 克隆项目

```bash
git clone <repository-url>
cd vmlab
```

### 3. 部署应用

#### 开发环境部署
```bash
# 使用部署脚本（推荐）
./deploy.sh dev

# 或者手动部署
docker-compose up -d
```

#### 生产环境部署
```bash
# 使用部署脚本（推荐）
./deploy.sh prod

# 或者手动部署
docker-compose -f docker-compose.prod.yml up -d
```

### 4. 访问应用

- 前端界面: http://localhost
- 后端API: http://localhost:8000/api/
- 管理后台: http://localhost:8000/admin/
- noVNC控制台: http://localhost:6080

## 配置说明

### 环境变量

开发环境可以使用`.env`文件：

```bash
cp .env.example .env
# 编辑.env文件设置必要的配置
```

生产环境使用Docker secrets，密钥文件存放在`secrets/`目录：

```
secrets/
├── secret_key.txt        # Django密钥
├── db_password.txt       # 数据库密码
├── redis_password.txt    # Redis密码
└── grafana_password.txt  # Grafana密码
```

### 主要配置项

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | Django密钥 | 自动生成 |
| `DEBUG` | 调试模式 | 开发环境：1，生产环境：0 |
| `ALLOWED_HOSTS` | 允许的主机 | localhost,127.0.0.1 |
| `DATABASE_URL` | 数据库连接字符串 | PostgreSQL |
| `REDIS_URL` | Redis连接字符串 | redis://redis:6379/0 |

## 服务说明

### 核心服务

1. **frontend**: Vue.js前端应用，使用Nginx提供静态文件服务
2. **backend**: Django后端API服务
3. **db**: PostgreSQL数据库
4. **redis**: Redis缓存服务

### 可选服务

1. **novnc**: noVNC Web控制台服务
2. **prometheus**: 监控数据收集
3. **grafana**: 监控数据可视化

## 管理命令

### 查看服务状态
```bash
./deploy.sh status
# 或
docker-compose ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 停止服务
```bash
./deploy.sh stop
# 或
docker-compose down
```

### 完全清理
```bash
./deploy.sh clean
# 或
docker-compose down -v --rmi all
```

### 数据库管理

```bash
# 运行数据库迁移
docker-compose exec backend python manage.py migrate

# 创建超级用户
docker-compose exec backend python manage.py createsuperuser

# 进入Django shell
docker-compose exec backend python manage.py shell

# 备份数据库
docker-compose exec db pg_dump -U vmlab vmlab > backup.sql

# 恢复数据库
docker-compose exec -T db psql -U vmlab vmlab < backup.sql
```

## 存储卷说明

### 持久化数据

- `postgres_data`: PostgreSQL数据库文件
- `redis_data`: Redis数据文件
- `./logs`: 应用日志文件
- `./media`: 用户上传的文件（虚拟机模板等）

### 主机挂载

- `/var/run/libvirt/libvirt-sock`: Libvirt socket（必需）
- `/var/lib/libvirt/images`: 虚拟机磁盘镜像存储

## 网络配置

### 默认网络

项目使用Docker Compose默认的bridge网络，所有服务可以通过服务名相互访问。

### 端口映射

| 服务 | 内部端口 | 外部端口 | 描述 |
|------|----------|----------|------|
| frontend | 80 | 80 | Web前端 |
| backend | 8000 | 8000 | API服务 |
| db | 5432 | 5432 | PostgreSQL |
| redis | 6379 | 6379 | Redis |
| novnc | 8080 | 6080 | noVNC控制台 |

## 监控和日志

### 应用日志

- Django日志: `./logs/django.log`
- Nginx日志: 通过`docker-compose logs frontend`查看
- 数据库日志: 通过`docker-compose logs db`查看

### 健康检查

所有服务都配置了健康检查：

```bash
# 检查所有服务健康状态
docker-compose ps

# 检查应用健康端点
curl http://localhost:8000/health/
```

### 监控（生产环境）

生产环境包含Prometheus + Grafana监控栈：

- Prometheus: 收集监控指标
- Grafana: 可视化监控数据（用户名：admin，密码见secrets/grafana_password.txt）

## 故障排除

### 常见问题

1. **libvirt权限问题**
   ```bash
   sudo usermod -a -G libvirt $USER
   newgrp libvirt
   ```

2. **端口冲突**
   ```bash
   # 检查端口占用
   sudo netstat -tlnp | grep :80
   sudo netstat -tlnp | grep :8000
   ```

3. **磁盘空间不足**
   ```bash
   # 清理Docker缓存
   docker system prune -a
   ```

4. **数据库连接失败**
   ```bash
   # 检查数据库容器状态
   docker-compose logs db
   ```

### 调试模式

开发环境可以启用调试模式：

```bash
# 编辑.env文件
DEBUG=1

# 重启服务
docker-compose restart backend
```

## 安全考虑

### 生产环境安全

1. **使用HTTPS**: 配置SSL证书和反向代理
2. **密钥管理**: 使用Docker secrets或外部密钥管理服务
3. **网络隔离**: 使用防火墙限制访问
4. **定期更新**: 保持系统和依赖的最新版本

### 备份策略

1. **数据库备份**: 定期备份PostgreSQL数据
2. **文件备份**: 备份media目录中的用户文件
3. **配置备份**: 备份Docker Compose文件和配置

## 扩展和定制

### 水平扩展

```bash
# 扩展后端服务实例
docker-compose up -d --scale backend=3
```

### 自定义配置

1. 修改`docker-compose.yml`文件
2. 自定义环境变量
3. 挂载自定义配置文件

### 插件开发

参考Django应用开发指南添加新功能模块。

## 支持

如果遇到问题，请：

1. 查看日志文件
2. 检查健康状态
3. 参考故障排除部分
4. 提交Issue到项目仓库
