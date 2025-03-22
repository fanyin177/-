from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta

from user.models import User, AuditLog
from vehicle.models import Vehicle, VehicleUsageRecord
from reservation.models import Reservation
from maintenance.models import MaintenanceRecord


@login_required
@user_passes_test(lambda u: u.is_admin or u.is_superuser)
def statistics_view(request):
    """数据统计视图，仅管理员可访问"""
    # 用户统计
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    admin_users = User.objects.filter(role='admin').count() + User.objects.filter(is_superuser=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    driver_users = User.objects.filter(role='driver').count()
    regular_users = User.objects.filter(role='user', is_superuser=False, is_staff=False).count()
    
    # 车辆统计
    total_vehicles = Vehicle.objects.count()
    available_vehicles = Vehicle.objects.filter(status='available').count()
    inuse_vehicles = Vehicle.objects.filter(status='in_use').count()
    maintenance_vehicles = Vehicle.objects.filter(status='maintenance').count()
    
    # 车辆使用次数统计
    total_usage_records = VehicleUsageRecord.objects.count()
    active_usage_records = VehicleUsageRecord.objects.filter(is_active=True).count()
    completed_usage_records = VehicleUsageRecord.objects.filter(is_active=False).count()
    
    # 预约统计
    total_reservations = Reservation.objects.count()
    pending_reservations = Reservation.objects.filter(status='pending').count()
    approved_reservations = Reservation.objects.filter(status='approved').count()
    completed_reservations = Reservation.objects.filter(status='completed').count()
    
    # 维护统计
    total_maintenance = MaintenanceRecord.objects.count()
    
    # 最近7天的统计数据
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=7)
    
    # 最近7天的用户注册
    new_users_7days = User.objects.filter(date_joined__gte=seven_days_ago).count()
    
    # 最近7天的车辆使用记录
    usage_records_7days = VehicleUsageRecord.objects.filter(created_at__date__gte=seven_days_ago).count()
    
    # 最近7天的维护记录
    maintenance_7days = MaintenanceRecord.objects.filter(created_at__date__gte=seven_days_ago).count()
    
    # 最近7天的审计日志
    audit_logs_7days = AuditLog.objects.filter(created_at__date__gte=seven_days_ago).count()
    
    # 按天统计最近7天的活动
    days = [(today - timedelta(days=i)) for i in range(7)]
    days.reverse()  # 按时间顺序排列
    
    daily_stats = []
    for day in days:
        day_start = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time()))
        day_end = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.max.time()))
        
        daily_stats.append({
            'date': day.strftime('%m-%d'),
            'new_users': User.objects.filter(date_joined__range=(day_start, day_end)).count(),
            'usage_records': VehicleUsageRecord.objects.filter(created_at__range=(day_start, day_end)).count(),
            'maintenance': MaintenanceRecord.objects.filter(created_at__range=(day_start, day_end)).count(),
            'audit_logs': AuditLog.objects.filter(created_at__range=(day_start, day_end)).count(),
        })
    
    context = {
        'user': request.user,
        'is_admin': request.user.is_admin or request.user.is_superuser,
        'is_staff': request.user.is_staff,
        'is_driver': request.user.is_driver,
        
        # 用户统计
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'staff_users': staff_users,
        'driver_users': driver_users,
        'regular_users': regular_users,
        
        # 车辆统计
        'total_vehicles': total_vehicles,
        'available_vehicles': available_vehicles,
        'inuse_vehicles': inuse_vehicles,
        'maintenance_vehicles': maintenance_vehicles,
        
        # 车辆使用次数统计
        'total_usage_records': total_usage_records,
        'active_usage_records': active_usage_records,
        'completed_usage_records': completed_usage_records,
        
        # 维护统计
        'total_maintenance': total_maintenance,
        
        # 最近7天统计
        'new_users_7days': new_users_7days,
        'usage_records_7days': usage_records_7days,
        'maintenance_7days': maintenance_7days,
        'audit_logs_7days': audit_logs_7days,
        
        # 按天统计
        'daily_stats': daily_stats,
    }
    
    return render(request, 'statistics.html', context) 