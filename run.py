#!/usr/bin/env python
"""
车辆管理系统快速启动脚本
"""
import os
import sys
import subprocess
import time
import webbrowser


def check_environment():
    """检查环境"""
    print("检查环境...")
    if not os.path.exists('venv'):
        print("未找到虚拟环境，正在创建...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("虚拟环境创建完成！")
    
    # 激活虚拟环境并安装依赖
    if sys.platform == 'win32':
        python_path = os.path.join('venv', 'Scripts', 'python.exe')
        pip_path = os.path.join('venv', 'Scripts', 'pip.exe')
    else:
        python_path = os.path.join('venv', 'bin', 'python')
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    if not os.path.exists(python_path):
        print(f"无法找到Python解释器: {python_path}")
        return False
    
    print("安装依赖...")
    subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
    return True


def setup_database():
    """创建数据库和超级用户"""
    print("初始化数据库...")
    
    if sys.platform == 'win32':
        python_path = os.path.join('venv', 'Scripts', 'python.exe')
    else:
        python_path = os.path.join('venv', 'bin', 'python')
    
    # 创建目录
    for directory in ['logs', 'media', 'media/avatars', 'media/vehicles', 'media/vehicle_docs']:
        os.makedirs(directory, exist_ok=True)
    
    # 数据库迁移
    subprocess.run([python_path, 'manage.py', 'makemigrations'], check=True)
    subprocess.run([python_path, 'manage.py', 'migrate'], check=True)
    
    # 检查是否存在超级用户
    result = subprocess.run(
        [python_path, 'manage.py', 'shell', '-c', 
         'from user.models import User; print(User.objects.filter(is_superuser=True).exists())'],
        capture_output=True, text=True, check=True
    )
    
    if 'True' not in result.stdout:
        print("\n初次运行，需要创建超级管理员账户...")
        subprocess.run([python_path, 'manage.py', 'createsuperuser'], check=True)
    
    # 加载初始数据
    load_initial_data(python_path)
    
    return True


def load_initial_data(python_path):
    """加载初始数据"""
    if os.path.exists('initial_data.json'):
        print("\n正在加载初始数据...")
        # 检查是否已有车辆类型数据
        result = subprocess.run(
            [python_path, 'manage.py', 'shell', '-c', 
             'from vehicle.models import VehicleType; print(VehicleType.objects.exists())'],
            capture_output=True, text=True, check=True
        )
        
        if 'True' not in result.stdout:
            subprocess.run([python_path, 'manage.py', 'loaddata', 'initial_data.json'], check=True)
            print("初始数据加载完成！")
        else:
            print("已存在初始数据，跳过加载。")
    else:
        print("未找到初始数据文件，跳过加载。")


def run_server():
    """运行开发服务器"""
    print("\n启动车辆管理系统...")
    
    if sys.platform == 'win32':
        python_path = os.path.join('venv', 'Scripts', 'python.exe')
    else:
        python_path = os.path.join('venv', 'bin', 'python')
    
    # 收集静态文件
    subprocess.run([python_path, 'manage.py', 'collectstatic', '--noinput'], check=True)
    
    # 打开浏览器
    time.sleep(1)
    webbrowser.open('http://127.0.0.1:8000/')
    
    # 启动服务器
    subprocess.run([python_path, 'manage.py', 'runserver'])


if __name__ == '__main__':
    try:
        if check_environment() and setup_database():
            run_server()
    except Exception as e:
        print(f"错误: {str(e)}")
        input("按任意键退出...")
        sys.exit(1) 