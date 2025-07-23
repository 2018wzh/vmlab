#!/bin/bash

# VMLab Docker部署脚本
# 用于快速部署VMLab虚拟化实验平台

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker和Docker Compose是否安装
check_dependencies() {
    print_message "检查依赖..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    print_message "依赖检查完成"
}

# 检查libvirt权限
check_libvirt() {
    print_message "检查libvirt权限..."
    
    if ! test -S /var/run/libvirt/libvirt-sock; then
        print_warning "libvirt socket不存在，请确保libvirt已安装并运行"
        print_warning "运行以下命令安装libvirt:"
        echo "  sudo apt-get install libvirt-daemon-system libvirt-clients"
        echo "  sudo systemctl enable --now libvirtd"
    fi
    
    if ! groups $USER | grep -q "libvirt"; then
        print_warning "当前用户不在libvirt组中"
        print_warning "运行以下命令添加用户到libvirt组:"
        echo "  sudo usermod -a -G libvirt $USER"
        echo "  newgrp libvirt"
    fi
}

# 创建必要的目录
create_directories() {
    print_message "创建必要的目录..."
    
    mkdir -p logs
    mkdir -p media
    mkdir -p secrets
    
    # 创建libvirt镜像目录（如果不存在）
    sudo mkdir -p /var/lib/libvirt/images
    sudo chown -R $USER:libvirt /var/lib/libvirt/images
    sudo chmod 775 /var/lib/libvirt/images
}

# 生成密钥文件
generate_secrets() {
    print_message "生成密钥文件..."
    
    if [ ! -f secrets/secret_key.txt ]; then
        python3 -c "import secrets; print(secrets.token_urlsafe(50))" > secrets/secret_key.txt
        print_message "生成Django密钥"
    fi
    
    if [ ! -f secrets/db_password.txt ]; then
        python3 -c "import secrets; print(secrets.token_urlsafe(32))" > secrets/db_password.txt
        print_message "生成数据库密码"
    fi
    
    if [ ! -f secrets/redis_password.txt ]; then
        python3 -c "import secrets; print(secrets.token_urlsafe(32))" > secrets/redis_password.txt
        print_message "生成Redis密码"
    fi
    
    if [ ! -f secrets/grafana_password.txt ]; then
        echo "admin" > secrets/grafana_password.txt
        print_message "生成Grafana密码（默认：admin）"
    fi
    
    chmod 600 secrets/*
}

# 部署应用
deploy() {
    local mode=$1
    
    if [ "$mode" = "prod" ]; then
        print_message "部署生产环境..."
        docker-compose -f docker-compose.prod.yml up -d
    else
        print_message "部署开发环境..."
        docker-compose up -d
    fi
    
    print_message "等待服务启动..."
    sleep 30
    
    # 运行数据库迁移
    print_message "运行数据库迁移..."
    if [ "$mode" = "prod" ]; then
        docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
        docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
    else
        docker-compose exec backend python manage.py migrate
        docker-compose exec backend python manage.py collectstatic --noinput
    fi
    
    # 创建超级用户（可选）
    read -p "是否创建Django超级用户？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ "$mode" = "prod" ]; then
            docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
        else
            docker-compose exec backend python manage.py createsuperuser
        fi
    fi
}

# 显示服务状态
show_status() {
    print_message "服务状态："
    docker-compose ps
    
    print_message ""
    print_message "访问地址："
    echo "  前端: http://localhost"
    echo "  后端API: http://localhost:8000/api/"
    echo "  管理后台: http://localhost:8000/admin/"
    echo "  noVNC: http://localhost:6080"
}

# 主函数
main() {
    echo "VMLab Docker部署脚本"
    echo "===================="
    
    # 解析命令行参数
    case $1 in
        "prod")
            MODE="prod"
            ;;
        "dev"|"")
            MODE="dev"
            ;;
        "status")
            show_status
            exit 0
            ;;
        "stop")
            print_message "停止服务..."
            docker-compose down
            exit 0
            ;;
        "clean")
            print_message "清理容器和镜像..."
            docker-compose down -v --rmi all
            exit 0
            ;;
        *)
            echo "用法: $0 [dev|prod|status|stop|clean]"
            echo "  dev    - 部署开发环境（默认）"
            echo "  prod   - 部署生产环境"
            echo "  status - 显示服务状态"
            echo "  stop   - 停止所有服务"
            echo "  clean  - 清理所有容器和镜像"
            exit 1
            ;;
    esac
    
    check_dependencies
    check_libvirt
    create_directories
    
    if [ "$MODE" = "prod" ]; then
        generate_secrets
    fi
    
    deploy $MODE
    show_status
    
    print_message "部署完成！"
}

# 执行主函数
main "$@"
