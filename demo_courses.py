#!/usr/bin/env python
"""
课程管理API演示脚本

此脚本演示了如何使用VMLab课程管理API的各种功能
"""

import requests
import json
from requests.auth import HTTPBasicAuth

# API基础配置
BASE_URL = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}

def get_token(username, password):
    """获取JWT Token"""
    url = f"{BASE_URL}/auth/login/"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["access"]
    return None

def create_course(token, course_data):
    """创建课程"""
    url = f"{BASE_URL}/courses/"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    response = requests.post(url, json=course_data, headers=headers)
    return response

def get_courses(token):
    """获取课程列表"""
    url = f"{BASE_URL}/courses/"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response

def get_course_detail(token, course_id):
    """获取课程详情"""
    url = f"{BASE_URL}/courses/{course_id}/"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response

def add_student_to_course(token, course_id, student_id):
    """向课程添加学生"""
    url = f"{BASE_URL}/courses/{course_id}/add_student/"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    data = {"student_id": student_id}
    response = requests.post(url, json=data, headers=headers)
    return response

def get_course_statistics(token, course_id):
    """获取课程统计"""
    url = f"{BASE_URL}/courses/{course_id}/statistics/"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response

def create_template(token, template_data):
    """创建虚拟机模板"""
    url = f"{BASE_URL}/templates/"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    response = requests.post(url, json=template_data, headers=headers)
    return response

def get_templates(token):
    """获取模板列表"""
    url = f"{BASE_URL}/templates/"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response

def demo_course_management():
    """演示课程管理功能"""
    print("=" * 60)
    print("VMLab 课程管理API演示")
    print("=" * 60)
    
    # 1. 获取管理员Token
    print("\n1. 登录管理员账户...")
    admin_token = get_token("admin", "adminpassword")
    if not admin_token:
        print("❌ 管理员登录失败！请确保服务器正在运行且管理员账户存在。")
        return
    print("✅ 管理员登录成功！")
    
    # 2. 创建课程
    print("\n2. 创建测试课程...")
    course_data = {
        "name": "计算机网络实验",
        "description": "计算机网络实验课程，包含路由交换、网络安全等实验内容"
    }
    response = create_course(admin_token, course_data)
    if response.status_code == 201:
        course = response.json()
        course_id = course["id"]
        print(f"✅ 课程创建成功！课程ID: {course_id}")
        print(f"   课程名称: {course['name']}")
        print(f"   课程描述: {course['description']}")
    else:
        print(f"❌ 课程创建失败: {response.status_code}")
        print(response.text)
        return
    
    # 3. 获取课程列表
    print("\n3. 获取课程列表...")
    response = get_courses(admin_token)
    if response.status_code == 200:
        courses = response.json()
        print(f"✅ 找到 {len(courses['results'])} 个课程:")
        for course in courses['results']:
            print(f"   - {course['name']} (ID: {course['id']})")
    else:
        print(f"❌ 获取课程列表失败: {response.status_code}")
    
    # 4. 获取课程详情
    print(f"\n4. 获取课程详情 (ID: {course_id})...")
    response = get_course_detail(admin_token, course_id)
    if response.status_code == 200:
        course_detail = response.json()
        print("✅ 课程详情:")
        print(f"   名称: {course_detail['name']}")
        print(f"   教师数量: {len(course_detail['teachers'])}")
        print(f"   学生数量: {len(course_detail['students'])}")
        print(f"   模板数量: {len(course_detail['vm_templates'])}")
    else:
        print(f"❌ 获取课程详情失败: {response.status_code}")
    
    # 5. 获取课程统计
    print(f"\n5. 获取课程统计...")
    response = get_course_statistics(admin_token, course_id)
    if response.status_code == 200:
        stats = response.json()
        print("✅ 课程统计:")
        print(f"   学生总数: {stats['total_students']}")
        print(f"   教师总数: {stats['total_teachers']}")
        print(f"   模板总数: {stats['total_templates']}")
        print(f"   虚拟机总数: {stats['total_vms']}")
        print(f"   运行中虚拟机: {stats['running_vms']}")
        print(f"   已停止虚拟机: {stats['stopped_vms']}")
    else:
        print(f"❌ 获取课程统计失败: {response.status_code}")
    
    # 6. 创建虚拟机模板
    print("\n6. 创建虚拟机模板...")
    template_data = {
        "name": "Ubuntu 20.04 LTS",
        "description": "Ubuntu 20.04 LTS服务器版，预装网络工具",
        "file_path": "/var/lib/libvirt/images/ubuntu20.04-server.qcow2",
        "course": course_id,
        "is_public": False
    }
    response = create_template(admin_token, template_data)
    if response.status_code == 201:
        template = response.json()
        print("✅ 虚拟机模板创建成功！")
        print(f"   模板名称: {template['name']}")
        print(f"   模板描述: {template['description']}")
        print(f"   文件路径: {template['file_path']}")
    else:
        print(f"❌ 模板创建失败: {response.status_code}")
        print(response.text)
    
    # 7. 获取模板列表
    print("\n7. 获取模板列表...")
    response = get_templates(admin_token)
    if response.status_code == 200:
        templates = response.json()
        print(f"✅ 找到 {len(templates['results'])} 个模板:")
        for template in templates['results']:
            print(f"   - {template['name']} (课程: {template['course_name']})")
    else:
        print(f"❌ 获取模板列表失败: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎉 课程管理API演示完成！")
    print("=" * 60)

if __name__ == "__main__":
    demo_course_management()
