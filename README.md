# 公司车辆管理系统

基于Python Django和MongoDB开发的公司车辆管理系统，提供车辆信息管理、预约使用、维护记录等功能。

## 技术栈

- 后端：Python 3.9+ + Django 4.2
- 数据库：MongoDB
- 认证：JWT
- API：Django REST framework
- 前端：Django模板 + Bootstrap5

## 功能特点

- 🚗 车辆信息管理：添加、修改、删除车辆信息
- 👥 用户管理：员工注册、权限控制
- 📅 车辆预约：在线预约、审批流程
- 🔧 维护记录：保养记录、维修历史
- 📊 数据统计：使用频率、维护成本分析

## 安装与使用

### 环境准备

```bash
# 克隆仓库
git clone https://github.com/your-username/vehicle-management-system.git
cd vehicle-management-system

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置数据库

1. 确保已安装并启动MongoDB服务
2. 在项目根目录创建`.env`文件并配置：

```
DEBUG=True
SECRET_KEY=your_secret_key
MONGO_URI=mongodb://localhost:27017/vehicle_management
```

### 运行项目

```bash
# 执行数据库迁移
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

访问 http://127.0.0.1:8000/ 使用系统

## 项目结构

```
vehicle_management/
├── manage.py
├── vehicle_system/          # 项目配置
├── vehicle/                 # 车辆管理应用
├── user/                    # 用户管理应用
├── reservation/             # 预约管理应用
├── maintenance/             # 维护记录应用
└── templates/               # 前端模板
```

## 许可证

MIT #   -  
 