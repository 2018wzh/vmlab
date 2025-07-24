# VMLab 虚拟化实验平台 - 详细实现路线图

## 项目概述
VMLab是一个基于Django和Libvirt的现代化虚拟机实验平台，专为教育环境设计。本文档详细描述了项目的实现步骤和开发计划。

### 📋 下一步计划
1. 完成核心UI组件库开发
2. 实现用户管理界面
3. 开发虚拟机管理界面
4. 集成noVNC Web控制台
5. 实现实时状态更新和WebSocket支持

## 开发阶段规划

### 第一阶段：基础设施搭建 📋

#### 1.1 项目环境初始化
- [x] **Django项目配置**
  - [x] 创建Django项目结构
  - [x] 配置settings.py（数据库、静态文件等）
  - [x] 配置URL路由
  - [x] 设置日志系统

- [x] **数据库设计**
  - [x] 设计用户模型（扩展Django User模型）
  - [x] 设计角色权限模型
  - [x] 设计课程相关模型
  - [x] 设计虚拟机相关模型
  - [x] 设计任务队列模型
  - [x] 创建数据库迁移文件

- [x] **Docker容器化**
  - [x] 编写Dockerfile
  - [x] 创建docker-compose.yml

### 第二阶段：用户管理系统 👥
#### 2.1 用户认证与授权
- [x] **基础用户功能**
  - [x] 用户注册功能
  - [x] 用户登录/登出功能

- [x] **角色权限系统**
  - [x] 定义角色模型（学生、教师、管理员）
  - [x] 实现基于角色的权限控制
  - [x] 创建权限装饰器
  - [x] 实现资源访问控制

#### 2.2 用户管理界面
- [ ] **管理员界面**
  - [x] 用户列表展示 (后端)
  - [x] 用户创建/编辑功能 (后端)
  - [x] 用户状态管理 (后端)
  - [ ] 用户搜索和过滤

- [x] **资源配额管理**
  - [x] 设计配额模型
  - [x] 实现CPU配额控制 (后端)
  - [x] 实现内存配额控制 (后端)
  - [x] 实现磁盘配额控制 (后端)

### 第三阶段：课程管理模块 📚
#### 3.1 课程基础功能
- [x] **课程CRUD操作**
  - [x] 课程创建功能
  - [x] 课程信息编辑
  - [x] 课程列表展示
  - [x] 课程删除功能
  - [x] 课程状态管理

- [x] **课程-用户关联**
  - [x] 学生选课功能
  - [x] 教师课程分配
  - [x] 课程成员管理
  - [x] 权限继承机制

#### 3.2 虚拟机模板管理
- [x] **模板上传功能**
  - [x] qcow2文件上传接口
  - [x] 文件完整性验证
  - [x] 模板元数据管理

- [x] **模板分配系统**
  - [x] 课程模板关联
  - [x] 学生模板访问权限


### 第四阶段：虚拟机管理核心 💻 ✅ **已完成**
#### 4.1 Libvirt集成 ✅
- [x] **虚拟化后端**
  - [x] Libvirt Python API集成
  - [x] KVM/QEMU支持
  - [x] 虚拟机配置管理（XML生成）
  - [x] 网络配置管理（MAC地址生成）
  - [x] 存储管理（qcow2磁盘）

- [x] **虚拟机操作**
  - [x] 虚拟机创建（异步处理）
  - [x] 虚拟机启动/停止
  - [x] 虚拟机暂停/恢复
  - [x] 虚拟机重启
  - [x] 虚拟机删除（含磁盘清理）

#### 4.2 资源监控 ✅
- [x] **实时监控**
  - [x] CPU使用率监控
  - [x] 内存使用监控
  - [x] 磁盘I/O监控
  - [x] 网络流量监控
  - [x] 虚拟机状态监控

- [x] **虚拟机服务层**
  - [x] 服务层架构设计
  - [x] 异步任务处理（线程池）
  - [x] 错误处理和状态管理
  - [x] 资源配额验证

#### 4.3 控制台访问 ✅
- [x] **VNC控制台**
  - [x] VNC端口管理
  - [x] VNC密码生成
  - [x] 控制台访问API

#### 4.4 虚拟机管理API ✅
- [x] **REST API**
  - [x] 虚拟机CRUD操作
  - [x] 虚拟机控制操作（启动/停止/重启等）
  - [x] 虚拟机状态查询
  - [x] 虚拟机监控数据API
  - [x] 控制台访问API
  - [x] 权限控制（基于角色）

### 第五阶段：前端界面开发 🎨

#### 5.1 项目基础搭建
- [ ] **环境初始化**
  - [ ] 使用Vite创建Vue 3项目 (npm create vue@latest vmlab-frontend)
  - [ ] 安装核心依赖：Vue 3.4+、TypeScript、Vue Router 4、Pinia
  - [ ] 安装UI框架：Vuetify 3.x (Material Design 3)
  - [ ] 安装HTTP库：Axios、@vueuse/core (组合式API工具)
  - [ ] 配置开发环境代理到后端API

- [ ] **项目结构设置**
  - [ ] 创建TypeScript目录结构（src/components、views、stores、api、types等）
  - [ ] 配置Vue Router 4路由系统
  - [ ] 初始化Pinia状态管理
  - [ ] 配置Vuetify 3主题（Material Design 3配色）
  - [ ] 设置ESLint + Prettier + TypeScript配置

#### 5.2 API集成层开发
- [ ] **API服务模块**
  - [ ] 创建axios实例配置（src/api/index.ts）
  - [ ] 定义API响应类型（src/types/api.ts）
  - [ ] 实现请求/响应拦截器（Token、错误处理）
  - [ ] 创建认证API模块（src/api/auth.ts）
  - [ ] 创建用户管理API模块（src/api/users.ts）
  - [ ] 创建课程管理API模块（src/api/courses.ts）
  - [ ] 创建虚拟机管理API模块（src/api/vms.ts）

- [ ] **状态管理设计**
  - [ ] 认证Store（src/stores/auth.ts - Pinia）
  - [ ] 用户Store（src/stores/users.ts）
  - [ ] 课程Store（src/stores/courses.ts）
  - [ ] 虚拟机Store（src/stores/vms.ts）
  - [ ] 通知Store（src/stores/notifications.ts）

#### 5.3 通用组件开发
- [ ] **基础组件库（Composition API + TypeScript）**
  - [ ] 数据表格组件（DataTable.vue - 使用&lt;script setup&gt;）
  - [ ] 表单组件集（FormInput.vue、FormSelect.vue等）
  - [ ] 对话框组件（ConfirmDialog.vue、FormDialog.vue）
  - [ ] 通知提示组件（NotificationSnackbar.vue）
  - [ ] 加载状态组件（LoadingSpinner.vue、LoadingOverlay.vue）
  - [ ] 定义组件Props类型接口

- [ ] **业务组件开发**
  - [ ] 虚拟机状态卡片（VMStatusCard.vue）
  - [ ] 资源使用图表（ResourceChart.vue - 使用Chart.js或ECharts）
  - [ ] 用户角色标签（UserRoleBadge.vue）
  - [ ] 文件上传组件（FileUpload.vue - 支持拖拽）

#### 5.4 布局框架实现
- [ ] **主布局组件（Composition API）**
  - [ ] 应用栏组件（AppBar.vue）
    - [ ] Logo和品牌标识
    - [ ] 全局搜索框（使用@vueuse/core的useDebounceFn）
    - [ ] 用户头像和下拉菜单
    - [ ] 深色模式切换按钮
  - [ ] 侧边导航栏（NavigationDrawer.vue）
    - [ ] 导航菜单项（动态路由生成）
    - [ ] 角色权限控制显示
    - [ ] 收起/展开功能（响应式状态）
  - [ ] 主布局容器（DefaultLayout.vue）
    - [ ] Vuetify 3 v-app结构
    - [ ] 响应式布局适配
    - [ ] 内容区域路由视图（Suspense包装）

#### 5.5 认证系统模块
- [ ] **登录注册页面（Composition API + TypeScript）**
  - [ ] 登录页面（Login.vue）
    - [ ] 响应式表单（useForm组合函数）
    - [ ] 表单验证（Vee-Validate或自定义验证）
    - [ ] "记住我"功能（localStorage）
    - [ ] 与`/api/auth/login/`接口集成
    - [ ] 加载状态和错误处理
  - [ ] 注册页面（Register.vue）
    - [ ] 多步骤表单组件
    - [ ] 用户信息输入（响应式验证）
    - [ ] 角色选择（学生/教师）
    - [ ] 与`/api/auth/register/`接口集成

- [ ] **认证状态管理（Pinia）**
  - [ ] JWT Token存储和刷新机制
  - [ ] 登录状态持久化（localStorage/sessionStorage）
  - [ ] 路由守卫实现（beforeEach）
  - [ ] 自动登出功能（Token过期检测）

#### 5.6 用户管理模块
- [ ] **用户列表管理**
  - [ ] 用户列表页面（UserList.vue）
    - [ ] 数据表格展示用户信息
    - [ ] 搜索和筛选功能
    - [ ] 分页控制
    - [ ] 与`/api/users/`接口集成
  - [ ] 用户详情页面（UserDetail.vue）
    - [ ] 用户基本信息展示
    - [ ] 配额信息显示
    - [ ] 角色管理功能

- [ ] **用户操作功能**
  - [ ] 创建用户对话框
  - [ ] 编辑用户信息
  - [ ] 配额管理界面
  - [ ] 角色分配功能

#### 5.7 课程管理模块
- [ ] **课程列表和详情**
  - [ ] 课程列表页面（CourseList.vue）
    - [ ] 表格式布局展示课程
    - [ ] 课程搜索和筛选
    - [ ] 新建课程按钮
    - [ ] 与`/api/courses/`接口集成
  - [ ] 课程详情页面（CourseDetail.vue）
    - [ ] 课程基本信息卡片
    - [ ] 成员管理标签页（学生、教师列表）
    - [ ] 虚拟机模板管理
    - [ ] 统计信息展示

- [ ] **课程成员管理**
  - [ ] 学生列表组件（StudentList.vue）
  - [ ] 添加学生对话框
  - [ ] 教师管理组件
  - [ ] 成员搜索和批量操作

- [ ] **模板管理功能**
  - [ ] 模板列表展示
  - [ ] 模板上传组件
  - [ ] 模板分配给课程
  - [ ] 与`/api/templates/`接口集成

#### 5.8 虚拟机管理模块
- [ ] **虚拟机列表展示**
  - [ ] 虚拟机列表页面（VMList.vue）
    - [ ] 卡片布局展示虚拟机
    - [ ] 状态指示器（运行/停止/暂停）
    - [ ] 快速操作按钮（启动/停止/重启）
    - [ ] 与`/api/vms/`接口集成
  - [ ] 虚拟机详情页面（VMDetail.vue）
    - [ ] 详细配置信息
    - [ ] 资源使用监控图表
    - [ ] 操作日志展示

- [ ] **虚拟机操作功能**
  - [ ] 创建虚拟机向导
    - [ ] 选择模板步骤
    - [ ] 配置资源（CPU、内存、磁盘）
    - [ ] 选择课程关联
    - [ ] 配额验证提示
  - [ ] 虚拟机控制组件
    - [ ] 启动/停止/重启按钮
    - [ ] 暂停/恢复功能
    - [ ] 删除确认对话框

- [ ] **资源监控展示**
  - [ ] 实时状态更新（与`/api/vms/{id}/status/`集成）
  - [ ] 性能指标图表（与`/api/vms/{id}/metrics/`集成）
  - [ ] CPU、内存、磁盘、网络使用率


#### 5.9 VNC控制台模块
- [ ] **VNC控制台集成（现代化方案）**
  - [ ] 安装noVNC或替代方案（@novnc/novnc）
  - [ ] VNC控制台组件（VNCConsole.vue）
    - [ ] 使用Composition API封装
    - [ ] WebSocket连接管理（useWebSocket from @vueuse/core）
    - [ ] 错误处理和重连机制
    - [ ] 与`/api/vms/{id}/console_vnc/`集成
  - [ ] 控制台功能增强
    - [ ] 全屏模式支持（Fullscreen API）
    - [ ] 快捷键处理（useEventListener）
    - [ ] 分辨率自适应（useResizeObserver）
    - [ ] 连接状态指示器

#### 5.10 WebSocket实时更新
- [ ] **WebSocket集成（@vueuse/core）**
  - [ ] 使用useWebSocket管理连接
  - [ ] 虚拟机状态实时更新
  - [ ] 资源监控数据推送
  - [ ] 系统通知推送
  - [ ] 自动断线重连机制
  - [ ] 心跳检测实现

#### 5.11 路由和权限控制
- [ ] **路由系统完善（Vue Router 4）**
  - [ ] 路由配置和嵌套路由（TypeScript定义）
  - [ ] 路由守卫实现（beforeEach、meta字段）
  - [ ] 基于角色的页面访问控制
  - [ ] 404页面和错误处理
  - [ ] 懒加载路由组件

- [ ] **权限控制实现**
  - [ ] 自定义指令v-permission
  - [ ] 组件级权限控制（Composition API）
  - [ ] 菜单项权限显示（computed属性）
  - [ ] 操作按钮权限控制
  - [ ] API调用权限验证

#### 5.12 样式和主题
- [ ] **UI样式完善（现代化设计）**
  - [ ] Vuetify 3主题定制（Material Design 3）
  - [ ] 深色模式支持（useTheme）
  - [ ] 响应式设计优化（CSS Grid + Flexbox）
  - [ ] 自定义CSS变量系统
  - [ ] 动画和过渡效果（Vue Transition）

#### 5.13 测试和优化
- [ ] **前端测试（现代化测试栈）**
  - [ ] 单元测试（Vitest + Vue Test Utils）
  - [ ] 组件测试（@vue/test-utils）
  - [ ] E2E测试（Playwright或Cypress）
  - [ ] TypeScript类型检查


### 第六阶段：系统优化与部署 🚀
#### 6.1 文档编写
- [ ] **技术文档**
  - [ ] API文档
  - [ ] 架构设计文档
  - [ ] 部署指南
  - [ ] 开发规范

- [ ] **用户文档**
  - [ ] 用户手册
  - [ ] 管理员指南
  - [ ] 常见问题解答
  - [ ] 视频教程
