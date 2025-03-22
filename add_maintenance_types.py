#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehicle_system.settings')
django.setup()

# 导入模型
from maintenance.models import MaintenanceType

# 定义常用的维护类型
maintenance_types = [
    {
        'name': '常规保养',
        'description': '包括机油更换、机油滤清器更换、空气滤清器检查等定期保养项目'
    },
    {
        'name': '轮胎更换',
        'description': '更换磨损或损坏的轮胎，保证行车安全'
    },
    {
        'name': '刹车系统检修',
        'description': '检查和维修刹车片、刹车盘、刹车油等刹车系统组件'
    },
    {
        'name': '发动机维修',
        'description': '发动机故障排查与维修，包括火花塞更换、燃油系统清洗等'
    },
    {
        'name': '电气系统维修',
        'description': '汽车电路、灯光、电池等电气系统的检查与维修'
    },
    {
        'name': '底盘维修',
        'description': '悬挂系统、转向系统等底盘部件的检修与调整'
    },
    {
        'name': '空调系统维修',
        'description': '空调系统检查、清洗、加氟等维护保养'
    },
    {
        'name': '年检前准备',
        'description': '车辆年检前的全面检查与维修，确保符合年检标准'
    },
    {
        'name': '事故维修',
        'description': '交通事故后的车身修复、零部件更换等维修工作'
    },
    {
        'name': '车身美容',
        'description': '车辆外观清洗、打蜡、内饰清洁等美容保养'
    },
]

# 添加维护类型
for type_info in maintenance_types:
    # 检查是否已存在
    existing = MaintenanceType.objects.filter(name=type_info['name']).first()
    if not existing:
        print(f"添加维护类型: {type_info['name']}")
        MaintenanceType.objects.create(
            name=type_info['name'],
            description=type_info['description']
        )
    else:
        print(f"维护类型已存在: {type_info['name']}")

print("\n维护类型添加完成！共有维护类型：", MaintenanceType.objects.count()) 