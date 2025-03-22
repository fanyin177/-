from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
import decimal

from .models import MaintenanceRecord, MaintenanceType, MaintenanceItem, MaintenanceAttachment
from vehicle.models import Vehicle
from user.models import User, AuditLog


@login_required
def maintenance_list_view(request):
    """维护记录列表视图"""
    # 获取所有维护记录
    maintenance_records = MaintenanceRecord.objects.all().order_by('-created_at')
    
    # 获取所有维护类型
    maintenance_types = MaintenanceType.objects.all()
    
    context = {
        'maintenance_records': maintenance_records,
        'maintenance_types': maintenance_types,
        'user': request.user,
        'is_admin': request.user.is_admin or request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'is_driver': request.user.is_driver,
    }
    return render(request, 'maintenance_list.html', context)


@login_required
@user_passes_test(lambda u: u.is_admin or u.is_superuser or u.is_staff)
def create_maintenance_view(request):
    """创建维护记录视图，仅管理员和员工可访问"""
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle_id')
        maintenance_type_id = request.POST.get('maintenance_type')
        description = request.POST.get('description')
        scheduled_date = request.POST.get('scheduled_date')
        estimated_cost_str = request.POST.get('estimated_cost', '')
        
        # 处理预估费用,如果为空则设置为None
        if not estimated_cost_str or estimated_cost_str.strip() == '':
            estimated_cost = None
        else:
            try:
                estimated_cost = Decimal(estimated_cost_str)
            except (ValueError, decimal.InvalidOperation):
                estimated_cost = None
        
        # 简单的表单验证
        if not all([vehicle_id, maintenance_type_id, description, scheduled_date]):
            messages.error(request, '请填写所有必填字段')
            # 获取所有车辆和维护类型，以便重新渲染表单
            vehicles = Vehicle.objects.all()
            maintenance_types = MaintenanceType.objects.all()
            
            context = {
                'vehicles': vehicles,
                'maintenance_types': maintenance_types,
                'user': request.user,
                'is_admin': request.user.is_admin or request.user.is_superuser,
                'is_staff': request.user.is_staff,
                'is_driver': request.user.is_driver,
            }
            return render(request, 'create_maintenance.html', context)
        
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            maintenance_type = MaintenanceType.objects.get(id=maintenance_type_id)
            
            # 创建维护记录
            record = MaintenanceRecord.objects.create(
                vehicle=vehicle,
                maintenance_type=maintenance_type,
                title=f"{vehicle.license_plate}的{maintenance_type.name}",
                description=description,
                start_date=scheduled_date,
                cost=estimated_cost,
                created_by=request.user
            )
            
            # 记录审计日志
            AuditLog.objects.create(
                user=request.user,
                action='create',
                resource='维护记录',
                details=f'创建了维护记录 #{record.id} 车辆:{vehicle.license_plate}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            messages.success(request, '维护记录已创建')
            return redirect('maintenance_list')
            
        except (Vehicle.DoesNotExist, MaintenanceType.DoesNotExist):
            messages.error(request, '所选车辆或维护类型不存在')
            # 获取所有车辆和维护类型，以便重新渲染表单
            vehicles = Vehicle.objects.all()
            maintenance_types = MaintenanceType.objects.all()
            
            context = {
                'vehicles': vehicles,
                'maintenance_types': maintenance_types,
                'user': request.user,
                'is_admin': request.user.is_admin or request.user.is_superuser,
                'is_staff': request.user.is_staff,
                'is_driver': request.user.is_driver,
            }
            return render(request, 'create_maintenance.html', context)
    
    # 获取所有可用的车辆
    vehicles = Vehicle.objects.all()
    maintenance_types = MaintenanceType.objects.all()
    
    # 获取URL参数中的车辆ID（如果有）
    vehicle_id = request.GET.get('vehicle_id')
    
    context = {
        'vehicles': vehicles,
        'maintenance_types': maintenance_types,
        'vehicle_id': vehicle_id,
        'user': request.user,
        'is_admin': request.user.is_admin or request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'is_driver': request.user.is_driver,
    }
    return render(request, 'create_maintenance.html', context)


@api_view(['GET'])
def index(request):
    """
    维护API入口点
    """
    return Response({
        'message': '维护记录API',
        'endpoints': {
            'maintenance_records': '/api/maintenance/list/',
            'maintenance_types': '/api/maintenance/types/',
        }
    }) 