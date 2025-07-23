# VMLab 虚拟化实验平台

<div align="center">

![VMLab Logo](https://img.shields.io/badge/VMLab-虚拟化实验平台-blue?style=for-the-badge)

[![Django](https://img.shields.io/badge/Django-5.2.4-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Libvirt](https://img.shields.io/badge/Libvirt-KVM/QEMU-red.svg)](https://libvirt.org/)
[![Material Design](https://img.shields.io/badge/UI-Material_Design-purple.svg)](https://material.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**现代化的虚拟机管理和实验教学平台**

[功能特色](#功能特色) • [快速开始](#快速开始) • [架构设计](#架构设计) • [部署指南](#部署指南) • [贡献指南](#贡献指南)

</div>

## 项目概述

VMLab是一个基于Django和Libvirt的现代化虚拟机实验平台，专为教育环境设计。它允许学生创建、管理和使用虚拟机完成实验任务，同时提供教师管理与查看学生虚拟机的功能。平台采用Material Design设计风格，提供直观易用的Web界面。

### 🎯 设计目标

- **教育优先**: 专为高校计算机实验教学设计
- **易于使用**: 直观的Material Design界面
- **高度可扩展**: 模块化架构，支持功能扩展
- **生产就绪**: 支持高并发和负载均衡
- **安全可靠**: 完善的权限控制和资源隔离

## 模块说明

### 👥 用户管理系统
- **多角色支持**: 学生、教师、管理员角色体系
- **资源配额**: 灵活的CPU、内存、磁盘配额管理
- **权限控制**: 基于角色的细粒度权限控制

### 💻 虚拟机管理
- **生命周期管理**: 创建、启动、停止、删除
- **实时监控**: 虚拟机状态和资源使用监控
- **控制台访问**: 基于noVNC和WebSSH的Web控制台

### 📚 课程管理
- **课程管理**: 完整的课程创建和管理功能
- **虚拟机分配**：教师可以将上传qcow2磁盘作为虚拟机模板供学生使用

## 技术栈
- **Web框架**: Django + Material Design
- **数据库**: SQLite
- **虚拟化**: Libvirt + KVM/QEMU
- **配置**: YAML

## 许可证

本项目基于MIT许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

<div align="center">

**如果这个项目对你有帮助，请给它一个⭐️**

Made with ❤️ by 2018wzh

</div>