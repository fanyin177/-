from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.urls import reverse

from .models import User, UserProfile, AuditLog


def home_view(request):
    """首页视图，重定向到车辆列表页面"""
    if request.user.is_authenticated:
        return redirect('vehicle_list')
    else:
        # 用户未登录，显示欢迎页面
        context = {
            'title': '欢迎使用公司车辆管理系统'
        }
        return render(request, 'index.html', context)


def login_view(request):
    """用户登录视图"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # 记录登录日志
            AuditLog.objects.create(
                user=user,
                action='login',
                resource='用户认证',
                details='用户登录系统',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            messages.success(request, f'欢迎回来，{user.username}！')
            return redirect('home')
        else:
            messages.error(request, '用户名或密码错误。')
    
    return render(request, 'login.html')


def logout_view(request):
    """用户退出视图"""
    if request.user.is_authenticated:
        # 记录退出日志
        AuditLog.objects.create(
            user=request.user,
            action='logout',
            resource='用户认证',
            details='用户退出系统',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
    
    logout(request)
    messages.success(request, '您已成功退出系统。')
    return redirect('home')


def register_view(request):
    """用户注册视图"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # 简单的表单验证
        if password != password2:
            messages.error(request, '两次输入的密码不一致。')
            return render(request, 'register.html')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在。')
            return render(request, 'register.html')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, '邮箱已被注册。')
            return render(request, 'register.html')
        
        # 创建新用户
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='user'  # 默认为普通用户角色
        )
        
        # 创建用户资料
        UserProfile.objects.create(user=user)
        
        # 记录注册日志
        AuditLog.objects.create(
            user=user,
            action='create',
            resource='用户',
            details='新用户注册',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        messages.success(request, f'账户创建成功！请登录。')
        return redirect('login')
    
    return render(request, 'register.html')


@login_required
def profile_view(request):
    """用户个人资料视图"""
    user = request.user
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    if request.method == 'POST':
        # 更新用户信息
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        user.save()
        
        # 更新用户资料
        profile.id_card = request.POST.get('id_card', profile.id_card)
        profile.emergency_contact = request.POST.get('emergency_contact', profile.emergency_contact)
        profile.emergency_phone = request.POST.get('emergency_phone', profile.emergency_phone)
        
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            user.save()
        
        profile.save()
        
        # 记录更新日志
        AuditLog.objects.create(
            user=user,
            action='update',
            resource='用户资料',
            details='用户更新个人资料',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        messages.success(request, '个人资料已更新！')
        return redirect('profile')
    
    context = {
        'user': user,
        'profile': profile
    }
    return render(request, 'profile.html', context)


@api_view(['GET'])
def index(request):
    """
    用户API入口点
    """
    return Response({
        'message': '用户管理API',
        'endpoints': {
            'users': '/api/users/list/',
            'profiles': '/api/users/profiles/',
            'audit_logs': '/api/users/audit-logs/',
        }
    })


@login_required
@user_passes_test(lambda u: u.is_admin or u.is_superuser or u.is_staff)
def user_management_view(request):
    """用户管理视图，仅管理员和员工可访问"""
    # 处理添加用户的POST请求
    if request.method == 'POST' and request.POST.get('action') == 'add_user':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        department = request.POST.get('department')
        phone = request.POST.get('phone')
        is_active = 'is_active' in request.POST
        
        # 验证基本字段
        if not all([username, email, password, role]):
            messages.error(request, '请填写所有必填字段')
            return redirect('user_management')
        
        # 检查用户名是否存在
        if User.objects.filter(username=username).exists():
            messages.error(request, f'用户名 {username} 已存在')
            return redirect('user_management')
        
        # 检查邮箱是否存在
        if User.objects.filter(email=email).exists():
            messages.error(request, f'邮箱 {email} 已被注册')
            return redirect('user_management')
            
        try:
            # 创建新用户
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # 设置附加信息
            user.role = role
            user.department = department
            user.phone = phone
            user.is_active = is_active
            
            # 根据角色设置权限
            if role == 'admin':
                if request.user.is_superuser:  # 只有超级管理员可以创建管理员
                    user.is_staff = True
            elif role == 'staff':
                user.is_staff = True
            elif role == 'driver':
                user.is_driver = True
                
            user.save()
            
            # 记录审计日志
            AuditLog.objects.create(
                user=request.user,
                action='create',
                resource='用户',
                resource_id=str(user.id),
                details=f'创建了新用户: {username}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            messages.success(request, f'用户 {username} 创建成功')
        except Exception as e:
            messages.error(request, f'创建用户失败: {str(e)}')
            
        return redirect('user_management')
    
    # 处理编辑用户的POST请求
    elif request.method == 'POST' and request.POST.get('action') == 'edit_user':
        user_id = request.POST.get('user_id')
        email = request.POST.get('email')
        role = request.POST.get('role')
        department = request.POST.get('department')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        is_active = 'is_active' in request.POST
        
        try:
            # 获取要编辑的用户
            target_user = get_object_or_404(User, id=user_id)
            
            # 防止非超级管理员修改超级管理员信息
            if target_user.is_superuser and not request.user.is_superuser:
                messages.error(request, '您没有权限修改超级管理员')
                return redirect('user_management')
            
            # 更新用户信息
            # 仅当邮箱变更，且已被其他用户使用时才拒绝更新
            if email != target_user.email and User.objects.filter(email=email).exclude(id=target_user.id).exists():
                messages.error(request, f'邮箱 {email} 已被其他用户使用')
                return redirect('user_management')
            
            target_user.email = email
            target_user.department = department
            target_user.phone = phone
            target_user.is_active = is_active
            
            # 处理角色变更
            # 重置所有角色标志
            target_user.is_staff = False
            target_user.is_driver = False
            
            if role == 'admin':
                if request.user.is_superuser:  # 只有超级管理员可以设置管理员
                    target_user.role = 'admin'
                    target_user.is_staff = True
            elif role == 'staff':
                target_user.role = 'staff'
                target_user.is_staff = True
            elif role == 'driver':
                target_user.role = 'driver'
                target_user.is_driver = True
            else:
                target_user.role = 'user'
            
            # 如果提供了新密码，则更新密码
            if password:
                target_user.set_password(password)
            
            target_user.save()
            
            # 记录审计日志
            AuditLog.objects.create(
                user=request.user,
                action='update',
                resource='用户',
                resource_id=str(target_user.id),
                details=f'更新了用户 {target_user.username} 的信息',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            messages.success(request, f'用户 {target_user.username} 的信息已更新')
        except Exception as e:
            messages.error(request, f'更新用户失败: {str(e)}')
        
        return redirect('user_management')
    
    # 处理删除用户的POST请求
    elif request.method == 'POST' and request.POST.get('action') == 'delete_user':
        user_id = request.POST.get('user_id')
        
        try:
            # 获取要删除的用户
            target_user = get_object_or_404(User, id=user_id)
            
            # 防止删除超级管理员
            if target_user.is_superuser:
                messages.error(request, '超级管理员不能被删除')
                return redirect('user_management')
            
            # 防止用户删除自己
            if str(target_user.id) == str(request.user.id):
                messages.error(request, '您不能删除自己的账户')
                return redirect('user_management')
            
            username = target_user.username
            
            # 记录审计日志
            AuditLog.objects.create(
                user=request.user,
                action='delete',
                resource='用户',
                resource_id=str(target_user.id),
                details=f'删除了用户: {username}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            # 删除用户
            target_user.delete()
            
            messages.success(request, f'用户 {username} 已被删除')
        except Exception as e:
            messages.error(request, f'删除用户失败: {str(e)}')
        
        return redirect('user_management')
    
    # 获取所有用户
    users = User.objects.all().order_by('-date_joined')
    
    # 最近注册的用户
    recent_users = User.objects.all().order_by('-date_joined')[:5]
    
    # 按角色统计
    admin_count = User.objects.filter(Q(role='admin') | Q(is_superuser=True)).count()
    staff_count = User.objects.filter(is_staff=True).exclude(Q(role='admin') | Q(is_superuser=True)).count()
    driver_count = User.objects.filter(role='driver').count()
    regular_count = User.objects.filter(role='user', is_superuser=False, is_staff=False).count()
    
    # 总用户数
    total_users = User.objects.count()
    
    context = {
        'users': users,
        'recent_users': recent_users,
        'total_users': total_users,  # 添加总用户数
        'admin_count': admin_count,
        'staff_count': staff_count,
        'driver_count': driver_count,
        'regular_count': regular_count,
        'user': request.user,
        'is_admin': request.user.is_admin or request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'is_driver': request.user.is_driver,
    }
    return render(request, 'user_management.html', context)


@login_required
@user_passes_test(lambda u: u.is_admin or u.is_superuser)
def edit_user_view(request, user_id):
    """编辑用户视图，仅管理员可访问"""
    target_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # 更新用户信息
        target_user.first_name = request.POST.get('first_name', target_user.first_name)
        target_user.last_name = request.POST.get('last_name', target_user.last_name)
        target_user.phone = request.POST.get('phone', target_user.phone)
        target_user.department = request.POST.get('department', target_user.department)
        target_user.position = request.POST.get('position', target_user.position)
        
        # 更新用户角色
        target_user.is_admin = 'is_admin' in request.POST
        target_user.is_staff = 'is_staff' in request.POST
        target_user.is_driver = 'is_driver' in request.POST
        target_user.is_active = 'is_active' in request.POST
        
        target_user.save()
        
        # 记录审计日志
        AuditLog.objects.create(
            user=request.user,
            action='update',
            resource='用户',
            details=f'管理员更新了用户 {target_user.username} 的信息',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        messages.success(request, f'用户 {target_user.username} 的信息已更新')
        return redirect('user_management')
    
    context = {
        'target_user': target_user,
        'user': request.user,
        'is_admin': request.user.is_admin or request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'is_driver': request.user.is_driver,
    }
    return render(request, 'edit_user.html', context)


@login_required
@user_passes_test(lambda u: u.is_admin or u.is_superuser)
def audit_logs_view(request):
    """审计日志视图，仅管理员可访问"""
    # 获取所有审计日志
    logs = AuditLog.objects.all().order_by('-created_at')
    
    # 按操作类型统计
    create_count = AuditLog.objects.filter(action='create').count()
    update_count = AuditLog.objects.filter(action='update').count()
    delete_count = AuditLog.objects.filter(action='delete').count()
    login_count = AuditLog.objects.filter(action='login').count()
    logout_count = AuditLog.objects.filter(action='logout').count()
    
    context = {
        'logs': logs,
        'create_count': create_count,
        'update_count': update_count,
        'delete_count': delete_count,
        'login_count': login_count,
        'logout_count': logout_count,
        'user': request.user,
        'is_admin': request.user.is_admin or request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'is_driver': request.user.is_driver,
    }
    return render(request, 'audit_logs.html', context)


@login_required
@user_passes_test(lambda u: u.is_admin or u.is_superuser)
def admin_iframe_view(request):
    """系统管理视图，在iframe中嵌入Django管理界面"""
    context = {
        'admin_url': reverse('admin:index'),
        'user': request.user,
        'is_admin': request.user.is_admin or request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'is_driver': request.user.is_driver,
        'active_page': 'admin_iframe'
    }
    return render(request, 'admin_iframe.html', context) 