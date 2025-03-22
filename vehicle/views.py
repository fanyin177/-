from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime

from .models import Vehicle, VehicleType, VehicleDocument, VehicleUsageRecord
from maintenance.models import MaintenanceRecord


@login_required
def vehicle_list_view(request):
    """车辆列表视图，显示所有可用车辆，支持条件筛选和排序"""
    # 初始查询集
    vehicles = Vehicle.objects.all()
    
    # 获取筛选条件
    license_plate = request.GET.get('license_plate', '')
    vehicle_type_id = request.GET.get('vehicle_type', '')
    status = request.GET.get('status', '')
    
    # 获取排序条件
    sort_by = request.GET.get('sort_by', '')
    sort_direction = request.GET.get('sort_direction', 'asc')
    
    # 根据筛选条件过滤车辆
    if license_plate:
        vehicles = vehicles.filter(license_plate__icontains=license_plate)
    
    if vehicle_type_id:
        vehicles = vehicles.filter(vehicle_type_id=vehicle_type_id)
    
    if status:
        vehicles = vehicles.filter(status=status)
    
    # 应用排序
    if sort_by:
        # 如果是降序，添加'-'前缀
        order_by_field = f"-{sort_by}" if sort_direction == 'desc' else sort_by
        vehicles = vehicles.order_by(order_by_field)
    else:
        # 默认排序为车牌号
        vehicles = vehicles.order_by('license_plate')
    
    # 分页
    page = request.GET.get('page', 1)
    per_page = 9  # 每页显示9辆车（3行3列）
    paginator = Paginator(vehicles, per_page)
    
    try:
        vehicles_page = paginator.page(page)
    except PageNotAnInteger:
        # 如果页码不是整数，返回第一页
        vehicles_page = paginator.page(1)
    except EmptyPage:
        # 如果页码超出范围，返回最后一页
        vehicles_page = paginator.page(paginator.num_pages)
    
    # 创建一个显示范围内的页码列表
    current_page = vehicles_page.number
    total_pages = paginator.num_pages
    
    # 确定要显示的页码范围
    if total_pages <= 7:
        # 如果总页数小于等于7，显示所有页码
        page_range = paginator.page_range
    else:
        # 显示当前页附近的页码和首尾页码
        if current_page <= 4:
            page_range = list(range(1, 6)) + [None, total_pages]
        elif current_page >= total_pages - 3:
            page_range = [1, None] + list(range(total_pages - 4, total_pages + 1))
        else:
            page_range = [1, None] + list(range(current_page - 1, current_page + 2)) + [None, total_pages]
    
    # 查询所有车辆类型用于筛选表单
    vehicle_types = VehicleType.objects.all()
    
    context = {
        'vehicles': vehicles_page,
        'vehicle_types': vehicle_types,
        'user': request.user,
        'is_admin': request.user.is_admin or request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'is_driver': request.user.is_driver,
        'total_vehicles': paginator.count,
        'page_range': page_range,
    }
    return render(request, 'vehicle_list.html', context)


@api_view(['GET'])
def index(request):
    """
    车辆API入口点
    """
    return Response({
        'message': '车辆管理API',
        'endpoints': {
            'vehicles': '/api/vehicles/list/',
            'vehicle_types': '/api/vehicles/types/',
            'vehicle_documents': '/api/vehicles/documents/',
        }
    })


@login_required
def vehicle_detail_view(request, vehicle_id):
    """车辆详情视图，显示单个车辆的详细信息"""
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
        
        # 获取车辆的维护记录
        maintenance_records = MaintenanceRecord.objects.filter(vehicle=vehicle).order_by('-created_at')
        
        # 获取车辆的文档
        documents = VehicleDocument.objects.filter(vehicle=vehicle)
        
        context = {
            'vehicle': vehicle,
            'maintenance_records': maintenance_records,
            'documents': documents,
            'user': request.user,
            'is_admin': request.user.is_admin or request.user.is_superuser,
            'is_staff': request.user.is_staff,
            'is_driver': request.user.is_driver,
        }
        return render(request, 'vehicle_detail.html', context)
    except Vehicle.DoesNotExist:
        messages.error(request, '所请求的车辆不存在')
        return redirect('vehicle_list')


@login_required
def register_usage_view(request, vehicle_id):
    """车辆使用登记视图，允许用户填写使用信息"""
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
        
        # 确保车辆当前状态为可用
        if vehicle.status != 'available':
            messages.error(request, '该车辆当前不可用于使用登记')
            return redirect('vehicle_detail', vehicle_id=vehicle_id)
        
        if request.method == 'POST':
            # 处理提交的表单数据
            purpose = request.POST.get('purpose', '')
            planned_return_date = request.POST.get('planned_return_date', '')
            destination = request.POST.get('destination', '')
            notes = request.POST.get('notes', '')
            
            # 验证数据
            if not purpose or not planned_return_date or not destination:
                messages.error(request, '请填写所有必填信息')
                context = {
                    'vehicle': vehicle,
                    'form_data': {
                        'purpose': purpose,
                        'destination': destination,
                        'planned_return_date': planned_return_date,
                        'notes': notes
                    }
                }
                return render(request, 'register_usage.html', context)
            
            try:
                # 转换日期格式
                planned_return_date = datetime.strptime(planned_return_date, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, '日期格式无效')
                context = {
                    'vehicle': vehicle,
                    'form_data': {
                        'purpose': purpose,
                        'destination': destination,
                        'planned_return_date': planned_return_date,
                        'notes': notes
                    }
                }
                return render(request, 'register_usage.html', context)
            
            # 更新车辆状态为使用中
            vehicle.status = 'in_use'
            vehicle.current_driver = request.user
            vehicle.save()
            
            # 创建使用记录
            VehicleUsageRecord.objects.create(
                vehicle=vehicle,
                user=request.user,
                purpose=purpose,
                planned_return_date=planned_return_date,
                destination=destination,
                notes=notes,
                start_mileage=vehicle.mileage
            )
            
            messages.success(request, '车辆使用登记成功！')
            return redirect('vehicle_list')  # 或者重定向到其他页面
        
        # GET 请求，显示表单
        context = {
            'vehicle': vehicle,
        }
        return render(request, 'register_usage.html', context)
    
    except Vehicle.DoesNotExist:
        messages.error(request, '所请求的车辆不存在')
        return redirect('vehicle_list')


@login_required
def return_vehicle_view(request, vehicle_id):
    """车辆归还视图，允许用户填写归还信息并完成使用记录"""
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
        
        # 确保车辆状态为使用中
        if vehicle.status != 'in_use':
            messages.error(request, '该车辆当前不在使用中，无法归还')
            return redirect('vehicle_detail', vehicle_id=vehicle_id)
        
        # 确保当前用户是车辆的使用者
        if vehicle.current_driver != request.user and not (request.user.is_admin or request.user.is_staff):
            messages.error(request, '您不是该车辆的当前使用者，无法归还')
            return redirect('vehicle_detail', vehicle_id=vehicle_id)
        
        # 获取当前活跃的使用记录
        try:
            usage_record = VehicleUsageRecord.objects.get(
                vehicle=vehicle, 
                user=vehicle.current_driver,
                is_active=True
            )
        except VehicleUsageRecord.DoesNotExist:
            messages.error(request, '找不到相关的使用记录')
            return redirect('vehicle_detail', vehicle_id=vehicle_id)
        
        if request.method == 'POST':
            # 处理提交的表单数据
            end_mileage = request.POST.get('end_mileage', '')
            notes = request.POST.get('notes', '')
            
            # 验证数据
            if not end_mileage:
                messages.error(request, '请填写结束里程')
                context = {
                    'vehicle': vehicle,
                    'usage_record': usage_record,
                    'form_data': {
                        'end_mileage': end_mileage,
                        'notes': notes
                    }
                }
                return render(request, 'return_vehicle.html', context)
            
            try:
                end_mileage = int(end_mileage)
                if end_mileage < usage_record.start_mileage:
                    messages.error(request, f'结束里程不能小于起始里程 ({usage_record.start_mileage} 公里)')
                    context = {
                        'vehicle': vehicle,
                        'usage_record': usage_record,
                        'form_data': {
                            'end_mileage': end_mileage,
                            'notes': notes
                        }
                    }
                    return render(request, 'return_vehicle.html', context)
            except ValueError:
                messages.error(request, '结束里程必须是一个有效的数字')
                context = {
                    'vehicle': vehicle,
                    'usage_record': usage_record,
                    'form_data': {
                        'end_mileage': end_mileage,
                        'notes': notes
                    }
                }
                return render(request, 'return_vehicle.html', context)
            
            # 更新使用记录的备注
            if notes:
                usage_record.notes = notes
                usage_record.save()
            
            # 完成使用记录
            usage_record.complete_usage(end_mileage)
            
            messages.success(request, '车辆归还成功！车辆状态已更新为可用。')
            return redirect('vehicle_list')  # 或者重定向到其他页面
        
        # GET 请求，显示表单
        context = {
            'vehicle': vehicle,
            'usage_record': usage_record,
        }
        return render(request, 'return_vehicle.html', context)
    
    except Vehicle.DoesNotExist:
        messages.error(request, '所请求的车辆不存在')
        return redirect('vehicle_list') 