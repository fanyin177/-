from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import Reservation, ReservationAttachment, TravelRecord
from vehicle.models import Vehicle
from user.models import User, AuditLog


@login_required
def reservation_list_view(request):
    """用户预约列表视图"""
    # 获取当前用户的预约
    user_reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')
    
    # 如果是管理员或员工，则可以看到所有预约
    if request.user.is_admin or request.user.is_superuser or request.user.is_staff:
        all_reservations = Reservation.objects.all().order_by('-created_at')
    else:
        all_reservations = None
    
    context = {
        'user_reservations': user_reservations,
        'all_reservations': all_reservations,
        'user': request.user,
        'is_admin': request.user.is_admin or request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'is_driver': request.user.is_driver,
    }
    return render(request, 'reservation_list.html', context)


@login_required
def create_reservation_view(request):
    """创建预约视图"""
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle_id')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        purpose = request.POST.get('purpose')
        
        # 简单的表单验证
        if not all([vehicle_id, start_time, end_time, purpose]):
            messages.error(request, '请填写所有必填字段')
            return redirect('vehicle_list')
        
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            
            # 检查车辆是否可用
            if vehicle.status != 'available':
                messages.error(request, '所选车辆当前不可用')
                return redirect('vehicle_list')
            
            # 创建预约
            reservation = Reservation.objects.create(
                user=request.user,
                vehicle=vehicle,
                start_time=start_time,
                end_time=end_time,
                purpose=purpose,
                start_location="默认出发地", # 添加必填字段
                destination="默认目的地",    # 添加必填字段
                status='pending'  # 初始状态为待审批
            )
            
            # 记录审计日志
            AuditLog.objects.create(
                user=request.user,
                action='create',
                resource='预约',
                details=f'创建了预约 #{reservation.id} 车辆:{vehicle.license_plate}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            messages.success(request, '预约申请已提交，等待审批')
            return redirect('reservation_list')
            
        except Vehicle.DoesNotExist:
            messages.error(request, '所选车辆不存在')
            return redirect('vehicle_list')
            
    # GET请求，显示预约表单
    vehicle_id = request.GET.get('vehicle_id')
    if vehicle_id:
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            context = {
                'vehicle': vehicle,
                'user': request.user,
                'is_admin': request.user.is_admin or request.user.is_superuser,
                'is_staff': request.user.is_staff,
                'is_driver': request.user.is_driver,
            }
            return render(request, 'create_reservation.html', context)
        except Vehicle.DoesNotExist:
            messages.error(request, '所选车辆不存在')
    
    return redirect('vehicle_list')


@login_required
def reservation_approval_view(request):
    """预约审批视图，仅管理员和员工可访问"""
    if not (request.user.is_admin or request.user.is_superuser or request.user.is_staff):
        messages.error(request, '您没有权限访问此页面')
        return redirect('home')
        
    # 获取所有待审批的预约
    pending_reservations = Reservation.objects.filter(status='pending').order_by('-created_at')
    
    # 获取最近审批过的预约
    recent_approved = Reservation.objects.filter(status__in=['approved', 'rejected']).order_by('-updated_at')[:10]
    
    context = {
        'pending_reservations': pending_reservations,
        'recent_approved': recent_approved,
        'user': request.user,
        'is_admin': request.user.is_admin or request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'is_driver': request.user.is_driver,
    }
    return render(request, 'reservation_approval.html', context)


@login_required
def approve_reservation(request, reservation_id):
    """审批预约"""
    if not (request.user.is_admin or request.user.is_superuser or request.user.is_staff):
        messages.error(request, '您没有权限执行此操作')
        return redirect('home')
        
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')
        
        if action == 'approve':
            reservation.status = 'approved'
            reservation.comment = comment
            reservation.approved_by = request.user
            
            # 更新车辆状态为使用中
            vehicle = reservation.vehicle
            vehicle.status = 'inuse'
            vehicle.save()
            
            # 记录审计日志
            AuditLog.objects.create(
                user=request.user,
                action='update',
                resource='预约',
                details=f'审批通过了预约 #{reservation.id} 车辆:{vehicle.license_plate}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            messages.success(request, f'预约 #{reservation.id} 已审批通过')
            
        elif action == 'reject':
            reservation.status = 'rejected'
            reservation.comment = comment
            reservation.approved_by = request.user
            
            # 记录审计日志
            AuditLog.objects.create(
                user=request.user,
                action='update',
                resource='预约',
                details=f'拒绝了预约 #{reservation.id} 车辆:{reservation.vehicle.license_plate}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            messages.success(request, f'预约 #{reservation.id} 已被拒绝')
            
        reservation.save()
    
    return redirect('reservation_approval')


@api_view(['GET'])
def index(request):
    """
    预约API入口点
    """
    return Response({
        'message': '预约管理API',
        'endpoints': {
            'reservations': '/api/reservations/list/',
            'user_reservations': '/api/reservations/user/',
            'pending': '/api/reservations/pending/',
        }
    }) 